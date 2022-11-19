from openapi3 import OpenAPI
from collections import defaultdict

from .api import METHODS
from .utils import iter_attrib, ext, map_type


class Controller(object):
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.routes = []


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

        for tag in self.get_tags():
            controller = Controller(tag.name, tag.description)
            controllers[tag.name] = controller

        for route_path, path in paths.items():
            for method, route_obj in iter_attrib(path, METHODS):
                if not route_obj.tags:
                    continue

                path_params = {
                    param.name: self.format_param(param)
                    for param in path.parameters
                    if param.in_ == 'path'
                }

                securities = self.get_security_schemes(route_obj)

                auth = [security.auth for security in securities.values()]
                if auth:
                    auth = ext(auth.pop(), 'auth-name')
                else:
                    auth = 'none'

                route_path = route_path.format(**path_params)
                # request_obj = get_request_object(route_obj)
                request_obj = None

                route = Route(
                    path=route_path,
                    params=path_params,
                    method=method,
                    type=ext(route_obj, 'router-type', 'plainjson'),
                    csrf=False,
                    auth=auth,
                    security=securities,
                    request=request_obj
                )

                for tag in route_obj.tags:
                    controllers[tag].routes.append(route)

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
