import importlib
import sys
import pytest
from mock import MagicMock
from types import ModuleType
from odoo_tools_openapi.loading import (
    find_odoo_hooks,
    remove_odoo_hooks,
    initialize_odoo_hooks,
    CustomOdooModuleFinder,
    OdooCustomLoader,
    CustomModule
)


class ModuleMock(MagicMock, ModuleType):
    @classmethod
    def new(cls):
        obj = MagicMock()
        obj.__class__ = cls
        return obj


def test_remove_init_hooks():
    found_hooks = find_odoo_hooks()
    assert len(found_hooks) == 1
    remove_odoo_hooks()
    found_hooks = find_odoo_hooks()
    assert len(found_hooks) == 0
    initialize_odoo_hooks()
    found_hooks = find_odoo_hooks()
    assert len(found_hooks) == 1


def test_custom_module():

    odoo_module = ModuleMock.new()
    odoo_module.__package__ = 'odoo.modules'
    odoo_module.__name__ = 'odoo.modules.registry'

    mod = CustomModule('odoo_tools_openapi.odoo.modules.registry')
    mod.__name__ = 'odoo_tools_openapi.odoo.modules.registry'
    mod.__odoo_version__ = 15
    mod.__prefix__ = 'odoo_tools_openapi.'

    with pytest.raises(AttributeError):
        mod.Registry

    mod.__patch_module__ = None

    with pytest.raises(AttributeError):
        mod.Registry

    mod.__odoo_module__ = odoo_module
    assert mod.Registry == odoo_module.Registry

    odoo_services = ModuleMock.new()
    odoo_services.__package__ = 'odoo.modules'
    odoo_services.__name__ = 'odoo.modules.services'
    odoo_services.fun = 1
    odoo_services.sys = sys
    sys.modules['odoo.modules.services'] = odoo_services
    odoo_module.services = odoo_services

    # Test custom module is loaded instead of actual module
    # available in attributes and can load attributes through
    # __odoo_module__ found
    assert 'services' not in dir(mod)
    assert mod.services != odoo_services
    assert isinstance(mod.services, CustomModule)
    assert mod.services.fun == 1
    assert mod.services.__odoo_module__ == odoo_services
    assert mod.services.sys == sys

    odoo_sql = ModuleMock.new()
    odoo_sql.__package__ = 'odoo.modules'
    odoo_sql.__name__ = 'odoo.modules.sql'
    odoo_sql.fun = 1
    odoo_sql.foo = 3
    sys.modules['odoo.modules.sql'] = odoo_sql
    odoo_module.sql = odoo_sql

    # Define custom module that should be loaded
    odoo_custom_sql = ModuleMock.new()
    mod_name = 'odoo_tools_openapi._odoo.common.odoo.modules.sql'
    odoo_custom_sql.__package__ = 'odoo_tools_openapi._odoo.custom.odoo'
    odoo_custom_sql.__name__ = mod_name
    odoo_custom_sql.fun = 2
    # prevent attribute from existing
    del odoo_custom_sql.foo
    sys.modules[mod_name] = odoo_custom_sql

    assert mod.sql.__odoo_module__ == odoo_sql
    assert mod.sql.__patch_module__ == odoo_custom_sql
    assert mod.sql.fun == 2
    assert mod.sql.foo == 3

    sql_mod = importlib.import_module('odoo_tools_openapi.odoo.modules.sql')
    assert sql_mod == mod.sql

    with pytest.raises(ModuleNotFoundError):
        importlib.import_module('odoo_tools_openapi.odoo.modules.fun')

    with pytest.raises(ModuleNotFoundError):
        from odoo_tools_openapi.odoo.modules import fun
        assert fun is not None
