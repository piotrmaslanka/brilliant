"""
Component decorator class
"""
import threading, uuid

class GlobalDatabase(object):
    """Brilliant's database of stuff"""
    
    CurrentScope = None
    Singletons = {}     # name => Singleton instance
    Sessions = {}       # name => Scope instance - session scopes
    ThreadLocal = threading.local()
    ThreadLocal.RequestScope = None     # current request scope
    ThreadLocal.SessionScope = None     # current session scope

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
        
    def __call__(self, cls):
        
        def instantiator(*args, **kwargs):
            inst = cls(*args, **kwargs)
            
            if self.scope == Component.SCOPE_SINGLETON:
                GlobalDatabase.Singletons[self.name] = inst
            elif self.scope == Component.SCOPE_SESSION:
                curSess = GlobalDatabase.ThreadLocal.SessionScope
                curSess.Objects[self.name] = inst
                                
            return inst
        
        return instantiator
    
class Session(object):
    """A session scope. This is a scope that will be created on demand, and will be
    deleted only when user wishes it. Use it like..
    
    session = Session.create()
    print 'Key is %s' % (session.key, )
    
    with session:
        ... use objects with session scope ...
        
    session.destroy()    
    """
    
    @staticmethod
    def create(self):
        key = uuid.uuid4().hex
        ss = Session(key)
        GlobalDatabase.Sessions[key] = ss
        return ss        
        
    def __init__(self, key):
        self.key = key
        self.Objects = {}
        
    @staticmethod
    def get(self, key):
        """Return a session scope by it's key
        @raise KeyError if does not exist"""
        return GlobalDatabase.Sessions[key]        
        
    def __enter__(self):
        """Pick this session as current context"""
        GlobalDatabase.ThreadLocal.SessionScope = self
        
    def __exit__(self):
        GlobalDatabase.ThreadLocal.SessionScope = None
        
    def destroy(self):
        """Destroy this session"""
        del GlobalDatabase.Sessions[self.key]
        
        