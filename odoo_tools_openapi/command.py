import click
from pathlib import Path
import requests
import yaml
from openapi3 import OpenAPI


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


@click.command()
@click.option('--url')
@click.option('--path')
def openapi(url, path):
    document = get_document(url, path)
    api = OpenAPI(document)

    with (Path.cwd() / 'api.yaml').open('w') as fout:
        data = yaml.safe_dump(
            document, allow_unicode=True, default_flow_style=False
        )
        fout.write(data)

    print(api)
