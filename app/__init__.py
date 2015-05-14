from brilliant.app.sessionExpirer import AutoExpirer

def setup(**kwargs):
    """
    Sets up a Brilliant enterprise application. Parameters may be
    
    session_auto_expire=True or session_auto_expire=30
        Sessions will automatically expire in 30 seconds, or amount specified
    """
    
    if 'session_auto_expire' in kwargs:
        if kwargs['session_auto_expire'] == True:
            AutoExpirer().start()
        else:
            AutoExpirer().start(kwargs['session_auto_expire'])