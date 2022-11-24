import sys
from .loading import initialize_odoo_hooks

initialize_odoo_hooks()


# odoo_module_name = f"{__name__}.odoo"
# sys.modules[odoo_module_name] = type(odoo_module_name, (CustomModule,), {})
