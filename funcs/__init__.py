import functools

def Listor(fun):
    """The same as @Postcall(list). Used to writing stuff that returns a list
    in a way that uses yield"""
    @functools.wraps(fun)
    def inside(*args, **kwargs):
        return list(fun(*args, **kwargs))
    return inside

def Postcall(function_to_call_later):
    """Invoke a function on result of wrapped function"""    
    def postcall_inside(fun):        
        @functools.wraps(fun)
        def relay(*args, **kwargs):
            return function_to_call_later(fun(*args, **kwargs))
        return relay
    return postcall_inside
        