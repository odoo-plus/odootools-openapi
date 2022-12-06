import sys
import importlib
import types
# from importlib import util
from importlib.abc import Loader, MetaPathFinder


class CustomModule(types.ModuleType):
    def __getattr__(self, name):

        if name == '__all__':
            if not hasattr(self.__odoo_module__, name):
                return [
                    attr for attr in dir(self.__odoo_module__)
                    if not attr.startswith('__')
                ]
        
        if name in ['__odoo_module__', '__patch_module__']:
            raise AttributeError(
                f"Couldn't load {name} from {self.__name__}"
            )

        if hasattr(self.__odoo_module__, name):
            obj = getattr(self.__odoo_module__, name)
            if self.__is_odoo_module(obj):
                return importlib.import_module(
                    f"{self.__prefix__}{obj.__name__}"
                )

        try:
            value = self.__get_odoo_property(name)
            setattr(self, name, value)
            return value
        except AttributeError as exc:
            raise

    def __is_odoo_module(self, obj):
        if not isinstance(obj, types.ModuleType):
            return False

        if not obj.__package__:
            return False

        if not obj.__package__.startswith('odoo'):
            return False

        return True

    def __get_odoo_property(self, name):
        try:
            return getattr(self.__patch_module__, name)
        except AttributeError:
            pass

        try:
            return getattr(self.__odoo_module__, name)
        except AttributeError:
            pass

        raise AttributeError(
            f"Module {self.__name__} doesn't have attribute {name}"
        )


class OdooCustomLoader(Loader):
    def __init__(self, finder, odoo_version, preload=False):
        super().__init__()
        self.finder = finder
        self.odoo_version = odoo_version
        self.preload = preload

    def create_module(self, spec):
        odoo_module = spec.name.replace(self.finder.base_module_replace, '')

        module = CustomModule(spec.name)
        module.__path__ = []
        module.__prefix__ = self.finder.base_module_replace
        module.__odoo_version__ = self.odoo_version
        module.__odoo_module__ = importlib.import_module(odoo_module)
        module.__patch_module__ = self.find_override_module(odoo_module)

        if not self.preload:
            return module

        return module



    # def preload_attributes(self):
    #     attrs = set(dir(module))

    #     inherited_mods = []

    #     if module.__patch_module__:
    #         inherited_mods.append(module.__patch_module__)

    #     if module.__odoo_module__:
    #         inherited_mods.append(module.__odoo_module__)

    #     for mod in inherited_mods:
    #         mod_attrs = set(dir(mod))
    #         missing_attrs = mod_attrs.difference(attrs)
    #         attrs = attrs.union(mod_attrs)
    #         for attr in missing_attrs:
    #             val = getattr(mod, attr)
    #             # Ignore imported module but should reimport odoo modules
    #             # this namespace
    #             if not isinstance(val, types.ModuleType):
    #                 setattr(module, attr, getattr(mod, attr))

    #     return module

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
            return importlib.machinery.ModuleSpec(
                fullname,
                self.loader,
            )

from pathlib import Path
from importlib.machinery import SourceFileLoader

class OdooCustomLoader2(Loader):
    def __init__(self, finder, odoo_version, preload=False):
        super().__init__()
        self.finder = finder
        self.odoo_version = odoo_version
        self.preload = preload
        self.base_path = finder.base_path

    def create_module(self, spec):
        odoo_module = spec.name.replace(self.finder.base_module_replace, '')

        module = CustomModule(spec.name)
        module.__path__ = []
        module.__prefix__ = '' # self.finder.base_module_replace
        module.__odoo_version__ = self.odoo_version

        module.__odoo_module__ = self.load_odoo_module(spec)
        module.__patch_module__ = None

        # self.preload_attributes(module)

        return module

    def preload_attributes(self, module):
        attrs = set(dir(module))

        inherited_mods = []

        if module.__patch_module__:
            inherited_mods.append(module.__patch_module__)

        if module.__odoo_module__:
            inherited_mods.append(module.__odoo_module__)

        for mod in inherited_mods:
            mod_attrs = set(dir(mod))
            missing_attrs = mod_attrs.difference(attrs)
            attrs = attrs.union(mod_attrs)
            for attr in missing_attrs:
                val = getattr(mod, attr)
                setattr(module, attr, getattr(mod, attr))

        return module

    def load_odoo_module(self, spec):
        base_path = self.base_path / "/".join(spec.name.split(".")[1:])

        if base_path.is_dir():
            base_path = base_path / '__init__.py'
        else:
            base_path = base_path.parent / f"{base_path.name}.py"

        return SourceFileLoader(spec.name, str(base_path)).load_module()


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


class FakeOdooLoader(MetaPathFinder):
    def __init__(self, base_module, base_path):
        super().__init__()
        self.base_module = base_module
        self.base_path = Path(base_path)
        self.base_length = len(base_module)
        self.base_module_replace = f"{self.base_module}."

        self.odoo_version = None

        self.loader = OdooCustomLoader2(self, self.odoo_version)

    def find_spec(self, fullname, path, target=None):

        if fullname.startswith(self.base_module_replace) or fullname == self.base_module:
            return importlib.machinery.ModuleSpec(
                fullname,
                self.loader
            )



def find_odoo_hooks():
    found_hooks = []
    for hook in sys.meta_path:
        if isinstance(hook, CustomOdooModuleFinder):
            found_hooks.append(hook)
    return found_hooks


def remove_odoo_hooks():
    to_remove = find_odoo_hooks()

    for finder in to_remove:
        sys.meta_path.remove(finder)


def initialize_odoo_hooks():
    odoo_spec = importlib.util.find_spec('odoo')
    if odoo_spec:
        sys.meta_path.insert(
            0, FakeOdooLoader('odoo', odoo_spec.submodule_search_locations[0])
        )

    sys.meta_path.insert(
        0, CustomOdooModuleFinder('odoo_tools_openapi')
    )
