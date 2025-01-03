from functools import wraps

def my_decorator(func):
    @wraps(func)
    def wrapper():
        """This will definitly get printed"""
        print("I am decorating this function")
        func()
        print("I have decorated it successfully")
    return wrapper

@my_decorator
def say_hello():
    """I dont think this will get printed"""
    print('Hello!')
    
say_hello()

print(say_hello.__name__) #It should come as wrapper
print(say_hello.__doc__)   #The wrapper docstring will get printed