import click
from collections import defaultdict
from jinja2 import Environment, BaseLoader, TemplateNotFound
from os.path import getmtime
from pathlib import Path


TYPE_MAP = {
    "integer": "int",
}

METHODS = ['get', 'delete', 'post', 'head', 'put']


def map_type(type_name):
    if type_name in TYPE_MAP:
        return TYPE_MAP[type_name]
    return type_name


def format_param(api, param):
    type_format = map_type(param.schema.type)

    if 'model' in param.extensions:
        ref = deref(api)(param.extensions['model']['$ref'])
        model_name = ref.extensions['model']
        type_format = "model({})".format(repr(model_name))

    param_name = param.name

    return '<{}:{}>'.format(type_format, param_name)


def deref(api):
    def dereference(path):
        return api._root.resolve_path(path.split('/')[1:])
    return dereference


def get_request_object(route):
    try:
        schema = route.requestBody.content['application/json'].schema
        return schema
    except Exception:
        return None


def get_controllers(api):
    controllers = defaultdict(list)

    for route_path, path in api.paths.items():
        for method in METHODS:
            route_obj = getattr(path, method)
            if not route_obj:
                continue

            if route_obj.tags:
                path_params = {
                    param.name: format_param(api, param)
                    for param in path.parameters
                    if param.in_ == 'path'
                }

                security = []
                for sec in route_obj.security or []:
                    scheme = api.components.securitySchemes[sec.name]
                    security.append((sec, scheme))

                route_path = route_path.format(**path_params)
                request_obj = get_request_object(route_obj)

                controllers[route_obj.tags[0]].append((
                    route_path,
                    method,
                    route_obj,
                    path,
                    security,
                    request_obj
                ))

    return controllers


class Loader(BaseLoader):
    def __init__(self, path):
        self.path = path

    def get_source(self, environment, template):
        template_path = self.path / template
        if not template_path.exists():
            raise TemplateNotFound(template)

        mtime = getmtime(template_path)

        source = template_path.open().read()

        return (
            source,
            str(template_path),
            lambda: mtime == getmtime(template_path)
        )


def get_rendering_context(api, controllers, tags, models):
    vals = dict(
        api=api,
        controllers=controllers,
        repr=repr,
        len=len,
        tags=tags,
        deref=deref(api),
        get_request_object=get_request_object,
        models=models
    )

    return vals


@click.command('model')
@click.argument('model')
@click.pass_context
def model(ctx, model):
    api = ctx.obj
    env = Environment(loader=Loader(Path.cwd()))
    controllers = get_controllers(api)
    tags = {
        tag.name: tag
        for tag in api.tags
    }
    template = env.get_template('models.jinja2')
    print(template.render(**get_rendering_context(api, controllers, tags, models=[model])))


@click.command('controller')
@click.argument('controller')
@click.pass_context
def controller(ctx, controller):
    api = ctx.obj
    env = Environment(loader=Loader(Path.cwd()))
    controllers = get_controllers(api)
    tags = {
        tag.name: tag
        for tag in api.tags
    }
    template = env.get_template('controllers.jinja2')
    controllers = {
        key: value
        for key, value in controllers.items()
        if key == controller
    }
    print(
        template.render(
            **get_rendering_context(api, controllers, tags, models=[])
        )
    )


@click.command('module')
@click.argument('module')
@click.pass_context
def module(ctx, module):
    module_path = Path.cwd() / module

    module_path.mkdir()

    controllers_path = module_path / 'controllers'
    api_models = module_path / 'api_models'

    controllers_path.mkdir()
    api_models.mkdir()

    api = ctx.obj
    env = Environment(loader=Loader(Path.cwd()))

    tags = {
        tag.name: tag
        for tag in api.tags
    }

    controllers = get_controllers(api)
    template = env.get_template('controllers.jinja2')

    def gen_init(path, modules):
        with path.open('w') as fout:
            for module in modules:
                fout.write(f"from . import {module}\n")

    import_modules = []

    for key, item in controllers.items():
        controller_file = template.render(
            **get_rendering_context(
                api,
                {key: item},
                tags,
                models=[]
            )
        )

        controller_path = controllers_path / f"{key.lower()}.py"
        with controller_path.open('w') as fout:
            fout.write(controller_file)

        import_modules.append(key.lower())

    controllers_import = controllers_path / "__init__.py"
    gen_init(controllers_import, import_modules)
    template = env.get_template('models.jinja2')

    import_modules = []
    for model in api.components.schemas.keys():
        model_file = api_models / f"{model.lower()}.py"

        model_data = template.render(
            **get_rendering_context(
                api, controllers, tags, models=[model]
            )
        )

        with model_file.open("w") as fout:
            fout.write(model_data)

        import_modules.append(model.lower())

    controllers_import = api_models / "__init__.py"
    gen_init(controllers_import, import_modules)
