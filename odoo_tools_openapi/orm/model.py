from collections import defaultdict
from .fields.base import BaseField


class DataStore(object):
    def __init__(self):
        self.__data = {}

    def set(self, name, value):
        self.__data[name] = value

    def get(self, name):
        return self.__data.get(name)

    def remove(self, name):
        if name in self.__data:
            del self.__data[name]


class MetaModel(object):
    pass


class PropertyLister(object):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.properties = set()

        for prop in cls.__get_properties():
            cls.properties.add(prop)

    @classmethod
    def __get_properties(cls):
        properties = set()

        for base in cls.__bases__:
            if (
                issubclass(base, PropertyLister) and
                base is not PropertyLister
            ):
                properties = properties.union(
                    base.properties
                )

        properties = properties.union(set([
            name
            for name, prop in cls.__dict__.items()
            if isinstance(prop, BaseField)
        ]))

        return properties


class JsonSerializable(PropertyLister):

    @classmethod
    def parse(cls, data):
        obj = cls()

        for prop in cls.properties:
            setattr(obj, prop, data.get(prop))

        return obj

    def to_json(self):
        data = {}
        for prop in self.properties:
            data[prop] = getattr(self, prop)
        return data


class ApiModel(JsonSerializable, MetaModel):
    subclasses = defaultdict(list)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses[cls.__module__].append(cls)

    def __init__(self):
        self._values = DataStore()
