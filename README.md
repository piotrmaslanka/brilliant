# Brilliant

Brilliant is a object scope tracker. That means you can have singletion-scoped objects, session-scoped objects, and so on. Essentially Brilliant is a Spring for Python, but without all that XML clumsiness, and just the juice.

## Components and Scopes
Component is a Python class that has a defined scope. Singleton scope is the default one - that means that component will be accessible from anywhere in the program. Session scope means that there will be a single (or none) object of certain kind for a session. Sessions can be created and destroyed at will. In order to use a session, it needs to be picked first.

Example with Singleton:

    from brilliant.objects import Component, wire
    
    @Component('my singleton')
    class Singleton(object):
        def __init__(self, val):
            self.value = val
            
    Singleton(5)
    
    wire('my singleton').value == 5
    
    
Example with session scoping:

    from brilliant.objects import Session, Component, wire
    
    @Component('user', scope=Component.SESSION_SCOPE)
    class User(object):
        def __init__(self, login):
            self.login = login
            
    def handle_Login(login):
        session = Session.create()
        with session:
            User(login)
        return session.key
        
        
    def check_with_key(key):
        with Session.get(key):
            print 'Login is %s' % (wire('user').login, )
            
    def logout(key):
        Session.get(key).destroy()
            