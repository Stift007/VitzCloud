class Traffic:
    def __init__(self,request) -> None:
        self.request = request
        self.form = request.form
        self.method = request.method

def raise_error(error):
    raise error

class Settings:
    def __init__(self,*,catch_requests=True,debug=False,methods=['GET'],timeout_after:float=60.0,on_error=raise_error,then=None):
        self.catch_r = catch_requests
        self.debug   = debug
        self.methods = methods
        self.timeout = timeout_after
        self.on_error = on_error
        self.after = then or self.on_error

    def set(self,name,value):
        self.__setattr__(name,value)

class Session(dict):
    def __init__(self):
        """Stores Information in a Dictionary filled with Strings and/or SessionLikes
        """
        super().__init__()

    def store(self,item,value):
        self.__setattr__(item,value)