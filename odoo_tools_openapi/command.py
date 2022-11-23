import click
from pathlib import Path
import requests
import yaml
# from openapi3 import OpenAPI
from .objects import OdooApi
from .rendering import get_environment, get_rendering_context


def get_document(url, path):
    if url:
        req = requests.get(url)
        data = req.content
    else:
        file_path = Path.cwd() / path
        with file_path.open('rb') as file:
            data = file.read()

    document = yaml.safe_load(data)
    return document


def output_module(api, env, dest_folder):
    init_file = dest_folder / '__init__.py'
    with init_file.open('w') as fout:
        fout.write("""from . import controllers""")

    manifest_file = dest_folder / '__manifest__.py'
    with manifest_file.open('w') as fout:
        fout.write("{}")

    output_controllers(api, env, dest_folder)
    output_models(api, env, dest_folder)


def template(template_name):
    def wrap(func):
        def proxy(*args, **kwargs):
            def render(env, filename):
                res = func(*args, **kwargs)
                ctx = get_rendering_context()

                if res:
                    ctx.update(res)

                template = env.get_template(template_name)
                with Path(filename).open('w') as fout:
                    fout.write(template.render(**ctx))

            return render
        return proxy
    return wrap


@template('api_model_init.jinja2')
def render_model_init(api):
    return {
        "api": api,
    }


@template('api_model.jinja2')
def render_model(api, model):
    return {
        "api": api,
        "model": model
    }


def output_models(api, env, dest_folder):
    models_folder = dest_folder / 'models'
    models_folder.mkdir(exist_ok=True)

    render_model_init(api)(
        env, models_folder / '__init__.py'
    )

    for model in api.models:
        render_model(api, model)(
            env, models_folder / f"{model.name.lower()}.py"
        )


def output_controllers(api, env, dest_folder):
    controllers_folder = dest_folder / 'controllers'
    controllers_folder.mkdir(exist_ok=True)
    controllers_init = controllers_folder / '__init__.py'

    controllers_tpl = env.get_template('controllers2.jinja2')
    controllers_init_tpl = env.get_template('controllers_init.jinja2')

    ctx = get_rendering_context()
    ctx['api'] = api
    with controllers_init.open('w') as fout:
        fout.write(controllers_init_tpl.render(**ctx))

    for key, controller in api.controllers.items():
        ctx = get_rendering_context()
        ctx['api'] = api
        ctx['controller'] = controller

        controller_file = controllers_folder / f"{key}.py"

        with controller_file.open('w') as fout:
            fout.write(controllers_tpl.render(**ctx))


@click.command()
@click.option('--url')
@click.option('--path')
@click.option('--destination', default='.')
def openapi(url, path, destination):
    document = get_document(url, path)

    api = OdooApi(document)
    env = get_environment()

    dest_folder = Path.cwd() / destination
    dest_folder.mkdir(exist_ok=True, parents=True)

    output_module(api, env, dest_folder)
