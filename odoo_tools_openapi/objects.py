class Controller(object):
    def __init__(self, name, routes):
        self.name = name
        self.routes = routes


class Route(object):
    def __init__(self, path, method):
        self.path = path
        self.method = method


class Schemas(object):
    def __init__(self, name, properties):
        self.name = name
        self.properties = properties
