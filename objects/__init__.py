"""
Component decorator class
"""
import threading, uuid, time, collections

class GlobalDatabase(object):
    """Brilliant's database of stuff"""
    
    CurrentScope = None
    Singletons = {}     # name => Singleton instance
    Sessions = {}       # name => Scope instance - session scopes
    ThreadLocal = threading.local()
    ThreadLocal.RequestScope = None     # current request scope
    ThreadLocal.SessionScope = None     # current session scope
    UsedSessions = collections.Counter()    # sessions being currently loaded

def wire(name):
    try:    # Look in GLOBAL scope
        return GlobalDatabase.Singletons[name]
    except KeyError:
        try:        # Look in SESSION scope
            return GlobalDatabase.ThreadLocal.SessionScope.Objects[name]
        except KeyError:
            pass
            
    raise NameError

class Component(object):
    """Use as a decorator to denote Brilliant components"""
    
    SCOPE_SINGLETON = 0
    SCOPE_SESSION = 1
        
    def __init__(self, name, **kwargs):
        self.name = name
        self.scope = kwargs.get('scope', Component.SCOPE_SINGLETON)
        
        Component.Local = threading.local()
        
    def __call__(self, ccls):
        
        class ComponentFactory(ccls):
            
            _brilliant_component_name = self.name
            
            def __new__(cls, *args, **kwargs):
                inst = ccls(*args, **kwargs)
                
                if self.scope == Component.SCOPE_SINGLETON:
                    GlobalDatabase.Singletons[self.name] = inst
                elif self.scope == Component.SCOPE_SESSION:
                    curSess = GlobalDatabase.ThreadLocal.SessionScope
                    curSess.Objects[self.name] = inst
                                    
                return inst
        
        return ComponentFactory
    
class Session(object):
    """A session scope. This is a scope that will be created on demand, and will be
    deleted only when user wishes it. Use it like..
    
        session = Session.create()
        print 'Key is %s' % (session.key, )
        
        with session:
            ... use objects with session scope ...
            
        session.destroy()
    
    If you want a session to automatically expire after not being used for some time, use
    session = Session.create(expire_in_second).
    A session that is currently being used will not expire
    """
    
    @staticmethod
    def create(**kwargs):
        key = uuid.uuid4().hex
        if 'expire' in kwargs:
            ss = Session(key, kwargs['expire'])
        else:
            ss = Session(key)
        GlobalDatabase.Sessions[key] = ss

        return ss        
        
    def __init__(self, key, expire=float('inf')):
        self.key = key
        self.Objects = {}
        self.expire_interval = expire
        self.expire_on = time.time() + expire     #: public to AutoExpirer
            
    @staticmethod
    def get(key):
        """Return a session scope by it's key
        @raise KeyError if does not exist"""
        return GlobalDatabase.Sessions[key]        
        
    def __enter__(self):
        """Pick this session as current context"""
        GlobalDatabase.ThreadLocal.SessionScope = self
        GlobalDatabase.UsedSessions.update((self, ))
        self.expire_on = time.time() + self.expire_interval
        
    def __exit__(self, a, b, c):
        self.expire_on = time.time() + self.expire_interval
        GlobalDatabase.ThreadLocal.SessionScope = None
        GlobalDatabase.UsedSessions.subtract((self, ))
        return False
        
    def destroy(self):
        """Destroy this session"""
        del GlobalDatabase.Sessions[self.key]
        
    def __hash__(self):
        return self.key.__hash__()
    
    def __eq__(self, other):
        return self.key == other.key
        
        