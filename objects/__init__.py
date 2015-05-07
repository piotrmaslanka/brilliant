"""
Component decorator class
"""
import threading

class GlobalDatabase(object):
    """Brilliant's database of stuff"""
    
    CurrentScope = None
    Singletons = {}     # name => Singleton instance
    ThreadLocal = threading.local()        # name => Scope instance    
    ThreadLocal.Scopes = []  ## list of scopes, from oldest (0) to newest (last)


def Autowire(name):
    try:
        return GlobalDatabase.Singletons[name]
    except KeyError:
        for scope in reversed(GlobalDatabase.ThreadLocal.Scopes):
            try:
                return scope.Objects[name]
            except KeyError:
                pass
            
    raise NameError

class Component(object):
    """Use as a decorator to denote Brilliant components"""
    
    SCOPE_SINGLETON = 0
        
    def __init__(self, name, **kwargs):
        self.name = name
        self.scope = kwargs.get('scope', Component.SCOPE_SINGLETON)
        
        Component.Local = threading.local()
        
    def __call__(self, cls):
        
        def instantiator(*args, **kwargs):
            inst = cls(*args, **kwargs)
            
            if self.scope == Component.SCOPE_SINGLETON:
                GlobalDatabase.Singletons[self.name] = inst
                                
            return inst
        
        return instantiator
        
        
class Scope(object):
    """Just a scope"""
    def __init__(self, name):
        self.name = name        
        self.Objects = {}       # name => instance

    def __enter__(self):
        """Enter a new scope"""
        GlobalDatabase.ThreadLocal.Scopes.append(self)
        
    def __exit__(self, a, b, c):
        del GlobalDatabase.ThreadLocal.Scopes[-1]
        return False
        