import yaml
import pytest
from click.testing import CliRunner


base = """openapi: 3.0.0
info:
  version: '1'
  title: ''
  description: ''
  contact:
    name: Loïc Faure-Lacroix
    url: https://www.odoo.plus
    email: info@odoo.plus
  license:
    name: Apache 2.0
    url: https://www.apache.org/licenses/LICENSE-2.0.html
"""


@pytest.fixture()
def basic_document():
    return yaml.safe_load(base)


simple_route_yaml = """
components:
  schemas:
    ApiResult:
      description: Api Result
      type: object
      properties:
        id:
          type: integer
          title: Resource Id
paths:
  /commands:
    get:
      description: get commands
      operationId: get_commands
      responses:
        200:
          description: Commands
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ApiResult"
"""


@pytest.fixture()
def simple_routes():
    return yaml.safe_load(simple_route_yaml)


@pytest.fixture()
def simple_openapi(basic_document, simple_routes, tmp_path):
    document = {}
    document.update(basic_document)
    document.update(simple_routes)

    document_file = tmp_path / 'document.yaml'

    doc_txt = yaml.safe_dump(document)
    with document_file.open('w') as fout:
        fout.write(doc_txt)

    return (document_file, document, doc_txt)


@pytest.fixture()
def runner():
    runner = CliRunner()
    return runner
