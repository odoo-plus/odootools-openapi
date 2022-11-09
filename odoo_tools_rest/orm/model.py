from collections import defaultdict


class ApiModel(object):
    subclasses = defaultdict(list)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses[cls.__module__].append(cls)

    @classmethod
    def parse(klass, data):
        obj = klass()

        for prop in klass.properties:
            setattr(obj, prop, data.get(prop))

        return obj

    def to_json(self):
        data = {}
        for prop in self.properties:
            data[prop] = getattr(self, prop)
        return data
