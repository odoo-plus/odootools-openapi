from openapi3 import OpenAPI
# from collections import defaultdict

from .api import METHODS
from .utils import iter_attrib, ext, map_type


class Controller(object):
    def __init__(self, api, name, description):
        self.api = api
        self.name = name
        self.description = description
        self.routes = []

    def add_route(self, path, route, method):
        path_params = {
            param.name: self.api.format_param(param)
            for param in path.parameters
            if param.in_ == 'path'
        }

        securities = self.api.get_security_schemes(route)

        auth = [security.auth for security in securities.values()]
        if auth:
            auth = auth.pop()
        if not auth:
            auth = 'none'

        # route_path = route_path.format(**path_params)
        # request_obj = get_request_object(route_obj)
        route_path = path.path[-1]
        request_obj = None

        route = Route(
            path=route_path,
            params=path_params,
            method=method,
            type=ext(route, 'router-type', 'plainjson'),
            csrf=False,
            auth=auth,
            security=securities,
            request=request_obj
        )

        self.routes.append(route)


class Route(object):
    def __init__(
        self,
        path,
        params,
        method,
        security,
        request,
        type='plainjson',
        csrf=False,
        auth='none',
    ):
        self.path = path
        self.method = method
        self.params = params
        self.type = type
        self.csrf = csrf
        self.auth = auth
        self.security = security
        self.request = request


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

    def format_param(self, param):
        type_format = map_type(param.schema.type)

        if 'model' in param.extensions:
            ref = self.deref(param.extensions['model']['$ref'])
            model_name = ref.extensions['model']
            type_format = "model({})".format(repr(model_name))

        param_name = param.name

        return '<{}:{}>'.format(type_format, param_name)

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
            for method, route in iter_attrib(path, METHODS):
                tags = []

                if not route.tags:
                    tags.append('default')
                else:
                    tags += route.tags

                for tag in tags:
                    controllers[tag].add_route(
                        path, route, method
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
