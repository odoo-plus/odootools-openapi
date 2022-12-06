from os import environ
import sys
from .loading import initialize_odoo_hooks

if environ.get('ODOO_AUTO_LOAD_IMPORT_HOOKS'):
    initialize_odoo_hooks()
