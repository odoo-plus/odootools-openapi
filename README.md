OdooTools OpenAPI
=================

This package is a library and an a plugin for [odoo-tools](https://github.com/llacroix/odoo-tools).

When used as a library, it define an orm that helps unwrap json body into python objects and Odoo
objects back into JSON.

When used as a command, it will generate an Odoo Module with api models and controllers as defined
in an openapi3 spec with custom extensions for Odoo.

The command can be invoked as such:

    odootools gen openapi --destination my_module_api --path path_to_spec
    odootools gen openapi --destination my_module_api --url url_to_spec

Then the module will be created inside the destination path. It will use
the title/description of the api to define the name/summary of the module.


Example API:

    openapi: 3.0.0
    info:
      contact:
        email: info@odoo.plus
        name: Loïc Faure-Lacroix
        url: https://www.odoo.plus
      description: ''
      license:
        name: Apache 2.0
        url: https://www.apache.org/licenses/LICENSE-2.0.html
      title: ''
      version: '1'

    tags:
      - name: projects
        description: Super projects

    components:
      schemas:
        ApiResult:
          description: Api Result
          properties:
            id:
              title: Resource Id
              type: integer
          type: object
        Project:
          description: Project
          x-model: project.project
          properties:
            id:
              title: ID
              type: integer
            name:
              title: Name
              type: string

    paths:
      /project/{project}:
        get:
          tags:
            - projects
          parameters:
            - name: project
              x-model:
                $ref: "#/components/schemas/Project"
              in: path
              required: true
              schema:
                type: integer
          description: Get a project
          operationId: get_project
          responses:
            200:
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/ApiResult'
              description: Project


Result controller:

    from odootools_openapi.odoo.http import request, route, Controller

    from ..api_models.apiresult import ApiResult


    class Projects(Controller):
        """
        Super projects
        """

        @route(
            route=["/project/<model('project.project'):project>"],
            methods=['GET'],
            csrf=False,
            type='plainjson',
            auth='none',
        )
        def get_project(self, project):
            """
            Get a project
            """
            pass
        
