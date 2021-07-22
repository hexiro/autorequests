class Parameter:

    def __init__(self, name: str, **kwargs):
        # isn't really used to it's full potential right now
        # we'll have to see if a good way to implement custom parameters is found
        self.__name = name
        # resolves <class 'str'> to str
        self.__default = repr(kwargs["default"]) if "default" in kwargs else None
        self.__typehint = kwargs["typehint"].__name__ if "typehint" in kwargs else None

    def __repr__(self):
        return f"<Parameter {self.code}>"

    @property
    def code(self):
        if self.typehint and self.default:
            return f"{self.name}: {self.typehint} = {self.default}"
        if self.typehint:
            return f"{self.name}: {self.typehint}"
        if self.default:
            return f"{self.name}={self.default}"
        return self.name

    @property
    def name(self):
        return self.__name

    @property
    def typehint(self):
        return self.__typehint

    @property
    def default(self):
        return self.__default
