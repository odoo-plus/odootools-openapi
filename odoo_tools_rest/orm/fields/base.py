class BaseField(property):
    def __init__(self, Type):
        super().__init__(
            BaseField.__get__,
            BaseField.__set__,
            BaseField.__delete__,
        )

    def __set_name__(self, owner, name):
        self.__name__ = name

    def __get__(self, owner, klass):
        return owner._values.get(self.__name__)

    def __set__(self, owner, value):
        owner._values.set(self.__name__, value)

    def __delete__(self, owner):
        owner._values.remove(self.__name__)
