import pytest
from jinja2 import Environment, TemplateNotFound
from odoo_tools_openapi.rendering import Loader
from odoo_tools_openapi.rendering import get_environment


def test_loader(tmp_path):
    loader = Loader(tmp_path)
    env = Environment(loader=loader)

    with pytest.raises(TemplateNotFound):
        env.get_template('template.jinja2')

    template = tmp_path / 'template.jinja2'
    with template.open('w') as fout:
        fout.write('hello')

    tpl = env.get_template('template.jinja2')
    assert tpl.render() == "hello"


def test_odoo_tools_env():
    env = get_environment()

    ctlrs = env.get_template('controllers.jinja2')
    models = env.get_template('models.jinja2')

    assert ctlrs is not None
    assert models is not None
