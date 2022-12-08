import sys
import importlib
import types
from pathlib import Path
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import SourceFileLoader


class NamespaceLoader(Loader):
    def __init__(self, paths=None):
        if paths is None:
            paths = []
        self.paths = paths

    def create_module(self, spec):
        module = types.ModuleType(spec.name)
        module.__path__ = self.paths[:]
        return module

    def exec_module(self, module):
        pass




class StackedModule(types.ModuleType):
    # def __setattr__(self, name, value):
    #    if isinstance(value, StackedModule):
    #        return
    #    return super().__setattr__(name, value)

    def __getattr__(self, name):
        if name == '__all__':
            if not hasattr(self.__orig__, name):
                return [
                    attr for attr in dir(self.__orig__)
                    if not attr.startswith('__')
                ]
        
        if name in ['__orig__', '__patch_module__']:
            raise AttributeError(
                f"Couldn't load {name} from {self.__name__}"
            )

        try:
            mod = getattr(self.__orig__, name)
            if isinstance(mod, StackedModule):
                return mod
            # mod = importlib.import_module(f"{self.__name__}.{name}")
            # print(f"Imported {self.__name__}.{name}")
            # setattr(self, name, mod)
            # return mod
        except AttributeError as exc:
            pass
        except FileNotFoundError as exc:
            pass
        except Exception as exc:
            pass
        
        # Check if the original module 
        # if hasattr(self.__orig__, name):
        #     obj = getattr(self.__orig__, name)

        #     if isinstance(obj, StackedModule):
        #         return obj

        #     if self.__is_origin_module(obj):
        #         mod_name = obj.__name__.replace('__stacked__.', '')
        #         mod = importlib.import_module(mod_name)
        #         # setattr(self, name, mod)
        #         return mod

        try:
            value = self.__get_patched_property(name)
            #if self.__name__ == 'odoo.tools' and name == 'config':
            #    import pdb; pdb.set_trace()
            setattr(self, name, value)
            # print(f"Setting {self.__name__}.{name}, {value}")
            return value
        except AttributeError as exc:
            raise

    def __is_origin_module(self, obj):
        if not isinstance(obj, types.ModuleType):
            return False

        if not obj.__package__:
            return False

        if not obj.__package__.startswith('__stacked__'):
            return False

        return True

    def __get_patched_property(self, name):
        check_modules = []
        check_modules += self.__patch_module__
        check_modules.append(self.__orig__)

        for mod in check_modules:
            try:
                result = getattr(mod, name)
                break
            except AttributeError:
                pass

        else:
            raise AttributeError(
                f"Module {self.__name__} doesn't have attribute {name}"
            )

        return result

    def __preload_attributes(self):
        attrs = set(dir(self))

        inherited_mods = []

        if module.__patch_module__:
            inherited_mods += module.__patch_module__

        if module.__orig__:
            inherited_mods.append(module.__orig__)

        for mod in inherited_mods:
            mod_attrs = set(dir(mod))
            missing_attrs = mod_attrs.difference(attrs)
            attrs = attrs.union(mod_attrs)
            for attr in missing_attrs:
                val = getattr(mod, attr)
                setattr(module, attr, getattr(mod, attr))

        return module


class StackedModuleLoader(Loader):
    def __init__(self, finder, extra_modules=None, preload=False):
        super().__init__()
        self.finder = finder
        self.preload = preload
        self.base_path = finder.base_path
        self.extra_modules = extra_modules

    def create_module(self, spec):
        odoo_module = spec.name.replace(self.finder.base_module_replace, '')

        module = StackedModule(spec.name)
        module.__path__ = []
        module.__orig__ = self.load_origin_module(spec)
        module.__patch_module__ = self.find_override_modules(spec)
        # sys.modules[spec.name] = module

        return module

    def exec_module(self, module):
        pass


    def load_origin_module(self, spec):
        base_path = self.base_path / "/".join(spec.name.split(".")[1:])

        if base_path.is_dir():
            base_path = base_path / '__init__.py'
        else:
            base_path = base_path.parent / f"{base_path.name}.py"

        # return importlib.import_module(f"__stacked__.{spec.name}")
        return SourceFileLoader(f"{spec.name}", str(base_path)).load_module()


    def find_override_modules(self, spec):
        modules = [
            f"{module}.{spec.name}"
            for module in (self.extra_modules or [])
        ]

        patch_modules = []

        for mod_name in modules:
            try:
                patch_modules.append(importlib.import_module(mod_name))
            except ModuleNotFoundError:
                pass

        return patch_modules

class StackedModuleOriginLoader(Loader):
    def __init__(self, finder, orig_name='__orig__'):
        super().__init__()
        self.finder = finder
        self.orig_length = len(orig_name) + 1

    def create_module(self, spec):
        module_name = spec.name[0:self.orig_length]
        stacked_module = importlib.import_module(module_name)
        return stacked_module.__orig__

    def exec_module(self, module):
        pass

import pdb

class StackedModuleFinder(MetaPathFinder):
    def __init__(self, base_module, base_path, extra_modules=None, exclude_modules=None):
        super().__init__()

        if exclude_modules is None:
            exclude_modules = []

        self.base_module = base_module
        self.base_path = Path(base_path)
        self.base_length = len(base_module)
        self.base_module_replace = f"{self.base_module}."
        self.exclude_modules = exclude_modules
        self.loader = StackedModuleLoader(
            self,
            extra_modules
        )
        # self.origin_loader = StackedModuleOriginLoader(
        #     self
        # )

    def find_spec(self, fullname, path, target=None):
        for module in self.exclude_modules:
            if fullname.startswith(module):
                return

        if fullname == '__stacked__':
            return importlib.machinery.ModuleSpec(
                fullname,
                NamespaceLoader()
            )

        if fullname.startswith(f"__stacked__.{self.base_module}.") or fullname == f"__stacked__.{self.base_module}":
            parts = fullname.split('.')[2:]
            base_path = self.base_path / "/".join(parts)

            if base_path.is_dir():
                base_path = base_path / '__init__.py'
            else:
                base_path = base_path.parent / f"{base_path.name}.py"

            spec = importlib.util.spec_from_file_location(fullname, str(base_path))

            return spec

        if (
            fullname.startswith(self.base_module_replace) or
            fullname == self.base_module
        ):
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


class OdooVersionedString(object):
    def __init__(self, template):
        self.template = template
        self.data = None

    def get_string(self):
        from odoo.release import version_info
        return self.template.format(version_info=version_info)

    def __str__(self):
        if not self.data:
            self.data = self.get_string()
        return self.data


class AddonsHookLoader(Loader):
    def __init__(self, addons_paths):
        self.addons_paths = addons_paths

    def create_module(self, spec):
        module_import = spec.name.split('.')[2:]

        module_file = "/".join(module_import)

        for path in self.addons_paths:
            module_path = Path(path) / module_file

            file_path = module_path / '__init__.py'
            if file_path.exists():
                break

            file_path = module_path.parent / f"{module_path.name}.py"
            if file_path.exists():
                break
        else:
            return

        return SourceFileLoader(
            spec.name,
            str(file_path)
        ).load_module()

    def exec_module(self, module):
        pass

class AddonsFinder(MetaPathFinder):
    def __init__(self, addons_paths):
        self.loader = AddonsHookLoader(addons_paths)

    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'odoo.addons':
            return importlib.machinery.ModuleSpec(
                fullname,
                NamespaceLoader(self.loader.addons_paths)
            )

        if fullname.startswith('odoo.addons.'):
            return importlib.machinery.ModuleSpec(
                fullname,
                self.loader
            )
    

def initialize_odoo_hooks():
    odoo_spec = importlib.util.find_spec('odoo')

    if odoo_spec:

        sys.meta_path.insert(
            0,
            StackedModuleFinder(
                'odoo',
                odoo_spec.submodule_search_locations[0],
                exclude_modules=[
                    "odoo.addons",
                ],
                extra_modules=[
                    OdooVersionedString("odoo_tools_openapi._odoo.v{version_info[0]}"),
                    "odoo_tools_openapi._odoo.common",
                ]
            )
        )

        sys.meta_path.insert(
            0,
            AddonsFinder([
                '/home/llacroix/work2/projects/odootools_rest/odoo_tools_openapi/venv/lib/python3.8/site-packages/odoo/addons'
            ])
        )
