import yaml
import pytest


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
