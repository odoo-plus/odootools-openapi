import sys
import importlib
import types
# from importlib import util
from importlib.abc import Loader, MetaPathFinder


class CustomModule(types.ModuleType):
    def __getattr__(self, name):
        if hasattr(self.__odoo_module__, name):
            obj = getattr(self.__odoo_module__, name)
            if self.__is_odoo_module(obj):
                raise AttributeError(
                    f"Couldn't load {name} from {self.__name__}"
                )
        return self.__load_odoo_property(name)

    def __is_odoo_module(self, obj):
        if not isinstance(obj, types.ModuleType):
            return False

        if not obj.__package__.startswith('odoo'):
            return False

        return True

    def __load_odoo_property(self, name):
        ret = None

        if self.__patch_module__ and hasattr(self.__patch_module__, name):
            ret = getattr(self.__patch_module__, name)

        if not ret and hasattr(self.__odoo_module__, name):
            ret = getattr(self.__odoo_module__, name)

        if ret:
            setattr(self, name, ret)
            return ret

        raise AttributeError(
            f"Module {self.__name__} doesn't have attribute {name}"
        )


class OdooCustomLoader(Loader):
    def __init__(self, finder, odoo_version):
        super().__init__()
        self.finder = finder
        self.odoo_version = odoo_version

    def create_module(self, spec):
        odoo_module = spec.name.replace(self.finder.base_module_replace, '')
        module = CustomModule(spec.name)
        module.__path__ = []
        module.__odoo_version__ = self.odoo_version
        module.__odoo_module__ = importlib.import_module(odoo_module)
        module.__patch_module__ = self.find_override_module(odoo_module)
        return module

    def find_override_module(self, odoo_module):
        obj = None

        mod_name_template = "{}._odoo.{}.{}"
        base_mod = self.finder.base_module

        versionned = mod_name_template.format(
            base_mod,
            f"v{self.odoo_version}",
            odoo_module
        )
        common = mod_name_template.format(
            base_mod,
            "common",
            odoo_module
        )

        for mod_name in [versionned, common]:
            try:
                obj = importlib.import_module(mod_name)
                break
            except ModuleNotFoundError:
                pass

        return obj

    def exec_module(self, module):
        pass


class CustomOdooModuleFinder(MetaPathFinder):
    def __init__(self, base_module):
        super().__init__()
        self.base_module = base_module
        self.base_odoo = f"{self.base_module}.odoo"
        self.base_module_replace = f"{self.base_module}."

        try:
            odoo = importlib.import_module('odoo', package='odoo')
            self.odoo_version = odoo.release.version_info[0]
        except ImportError:
            self.odoo_version = None

        self.loader = OdooCustomLoader(self, self.odoo_version)

    def find_spec(self, fullname, path, target=None):
        if fullname.startswith(self.base_odoo):
            try:
                return importlib.machinery.ModuleSpec(
                    fullname,
                    self.loader,
                )
            except ImportError as exc:
                pass


def initialize_odoo_hooks():
    sys.meta_path.insert(
        0, CustomOdooModuleFinder('odoo_tools_openapi')
    )
