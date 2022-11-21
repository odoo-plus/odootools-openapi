from jinja2 import (
    Environment,
    BaseLoader,
    ChoiceLoader,
    PackageLoader,
    TemplateNotFound,
)
from os.path import getmtime


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


def get_environment():
    loader = ChoiceLoader([
        PackageLoader('odoo_tools_openapi', 'templates'),
    ])

    env = Environment(
        loader=loader
    )

    return env
