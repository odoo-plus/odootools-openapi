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
