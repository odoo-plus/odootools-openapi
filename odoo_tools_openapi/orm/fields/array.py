from .base import BaseField


class Array(BaseField):
    def __init__(self, string, model):
        super().__init__(string)
        self.__model = model
