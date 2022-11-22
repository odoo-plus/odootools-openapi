import yaml
# from openapi3 import OpenAPI
# from odoo_tools_openapi.api import get_security_schemes
from odoo_tools_openapi.objects import OdooApi

routes = """
components:
  securitySchemes:
    management:
      type: http
      scheme: Bearer
      x-auth-name: jwt

    m2:
      type: http
      scheme: Bearer
      x-auth-name: jwt2

security:
  - management: []

paths:
  /projects:
    get:
      responses:
        200:
          description: Test Project
          content:
            application/json:
              schema:
                type: object
                properties: {}

  /projects/2:
    get:
      security:
        - m2: []
      responses:
        200:
          description: Test Project
          content:
            application/json:
              schema:
                type: object
                properties: {}
"""


def test_openapi_security(basic_document):
    api_yaml = yaml.safe_load(routes)
    api_yaml.update(basic_document)
    api = OdooApi(api_yaml)

    sec = api.get_security_schemes(api.api)
    assert len(sec) == 1

    sec = sec[0]

    assert sec.name == "management"
    assert sec.scheme == "Bearer"
    assert sec.type == "http"
    assert sec.auth == "jwt"

    # Check management on empty route has globally defined ones
    sec = api.get_security_schemes(api.api.paths['/projects'].get)
    assert len(sec) == 1

    sec = sec[0]

    assert sec.name == "management"
    assert sec.scheme == "Bearer"
    assert sec.type == "http"
    assert sec.auth == "jwt"

    sec = api.get_security_schemes(api.api.paths['/projects/2'].get)
    assert len(sec) == 1
    sec = sec[0]

    assert sec.name == "m2"
