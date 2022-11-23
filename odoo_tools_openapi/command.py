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
    render_manifest(api)(env, dest_folder / '__manifest__.py')
    render_module_init()(env, dest_folder / '__init__.py')

    output_models(api, env, dest_folder)
    output_controllers(api, env, dest_folder)


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


@template('module_init.jinja2')
def render_module_init():
    return {
    }


@template('manifest.jinja2')
def render_manifest(api):
    return {
        "api": api,
    }


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


@template('controllers_init.jinja2')
def render_ctl_init(api):
    return {
        "api": api
    }


@template('controllers2.jinja2')
def render_ctl_controller(api, controller):
    return {
        "api": api,
        "controller": controller
    }


def output_models(api, env, dest_folder):
    models_folder = dest_folder / 'api_models'
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

    render_ctl_init(api)(env, controllers_folder / '__init__.py')

    for key, controller in api.controllers.items():
        if len(controller.routes) == 0:
            continue

        render_ctl_controller(api, controller)(
            env, controllers_folder / f"{key}.py"
        )


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
