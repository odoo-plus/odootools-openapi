import yaml
from odoo_tools_openapi.objects import OdooApi

tags = """
components:

tags:
    - name: project
      description: Projects
    - name: instance
      description: Instances

paths:
"""

tags_parsed = """
components:

tags:
    - name: project
      description: Projects
    - name: instance
      description: Instances

paths:
  /projects:
    get:
      tags:
        - project
      responses:
        200:
          description: Test Project
          content:
            application/json:
              schema:
                type: object
                properties: {}

  /projects/{project}:
    parameters:
       - name: project
         in: path
         required: true
         schema:
           type: integer
    get:
      tags:
        - project
      responses:
        200:
          description: Test Project
          content:
            application/json:
              schema:
                type: object
                properties: {}
"""


def test_controller_tags(basic_document):
    doc = yaml.safe_load(tags)
    doc.update(basic_document)

    api = OdooApi(doc)

    assert len(api.controllers) == 2
    assert api.controllers['project'].description == "Projects"
    assert api.controllers['instance'].description == "Instances"
    assert len(api.controllers['project'].routes) == 0
    assert len(api.controllers['instance'].routes) == 0


def test_controllers_parsed(basic_document):
    doc = yaml.safe_load(tags_parsed)
    doc.update(basic_document)

    api = OdooApi(doc)

    assert len(api.controllers) == 2

    project_ctl = api.controllers['project']
    assert len(project_ctl.routes) == 2

    route = project_ctl.routes[0]

    assert route.path == "/projects"
    assert route.auth == 'none'
    assert route.method == 'get'
    assert route.params == {}
    assert route.csrf is False

    route2 = project_ctl.routes[1]

    assert route2.params == {'project': '<int:project>'}
