from openapi3 import OpenAPI
# from collections import defaultdict

from .api import METHODS
from .utils import iter_attrib, ext, map_type


class Parameters(object):
    def __init__(self, api, parameters=None):
        self.api = api
        if parameters is None:
            parameters = []

        self.parameters = parameters

    def inherit(self):
        return Parameters(self.api, self.parameters[:])

    def extend_with(self, params):
        result = self.inherit()
        result.parameters += params
        return result

    def format_param(self, param):
        type_format = map_type(param.schema.type)

        if 'model' in param.extensions:
            ref = self.api.deref(param.extensions['model']['$ref'])
            model_name = ref.extensions['model']
            type_format = "model({})".format(repr(model_name))

        param_name = param.name

        return '<{}:{}>'.format(type_format, param_name)

    def to_json(self):
        return {
            param.name: self.format_param(param)
            for param in self.parameters
        }


class Controller(object):
    def __init__(self, api, name, description):
        self.api = api
        self.name = name
        self.description = description
        self.routes = []

    def add_route(self, path, route, method, parameters):
        params = parameters.extend_with(route.parameters)

        route = Route(
            controller=self,
            route_obj=route,
            path_obj=path,
            params=params,
            method=method,
            csrf=False,
        )

        self.routes.append(route)


class Route(object):
    def __init__(
        self,
        controller,
        path_obj,
        route_obj,
        params,
        method,
        csrf=False,
    ):
        self.controller = controller
        self.api = controller.api
        self._path = path_obj
        self._route = route_obj
        self._params = params
        self.method = method
        self.type = type
        self.csrf = csrf

    @property
    def securities(self):
        return self.api.get_security_schemes(self._route)

    @property
    def path(self):
        return self._path.path[-1]

    @property
    def auth(self):
        securities = self.securities
        if len(securities) > 0:
            return securities.name
        else:
            return 'none'

    @property
    def params(self):
        return self._params.to_json()


class Schemas(object):
    def __init__(self, name, properties):
        self.name = name
        self.properties = properties


class ApiDocuent(object):
    def __init__(self, api):
        self.api = api


class Security(object):
    def __init__(self, name, type, scheme, auth):
        self.name = name
        self.scheme = scheme
        self.auth = auth
        self.type = type


class OdooApi(object):
    def __init__(self, doc):
        self.api = OpenAPI(doc)
        self.controllers = self.get_controllers()

    def deref(self, reference):
        return self.api._root.resolve_path(reference.split('/')[1:])


    def get_tags(self):
        tags = self.api.tags or []
        return tags

    def get_controllers(self):
        controllers = dict()

        paths = self.api.paths or {}

        controllers['default'] = Controller(
            self,
            'default',
            'Default Controller'
        )

        for tag in self.get_tags():
            controller = Controller(self, tag.name, tag.description)
            controllers[tag.name] = controller

        for route_path, path in paths.items():
            params = Parameters(self, path.parameters)

            for method, route in iter_attrib(path, METHODS):
                tags = []

                if not route.tags:
                    tags.append('default')
                else:
                    tags += route.tags

                for tag in tags:
                    controllers[tag].add_route(
                        path,
                        route,
                        method,
                        params,
                    )

        return controllers

    def get_security_schemes(self, obj):
        securities = {}

        for security in obj.security:
            name = security.name
            scheme = self.api.components.securitySchemes[name]

            sec = Security(
                name,
                scheme.type,
                scheme.scheme,
                ext(scheme, 'auth-name', 'none'),
            )

            securities[name] = sec

        return securities
