import sys
from types import ModuleType
from pathlib import Path
import time
from contextlib import contextmanager
import importlib
from odoo_tools.api.environment import Environment
from odoo_tools.app.plugins import (
    InitOdooPlugin,
    AddonsPathPlugin,
    OverlayModulePlugin,
    LoggingPlugin,
    FileLogPlugin,
    StreamLogPlugin,
    OdooWSGIHandler,
    BaseOdooApp,
    SessionStorePlugin,
    DbRoutePlugin,
)
from odoo_tools.app import OdooApplication
from pyinstrument import Profiler
from overlaymodule import OverlayFinder


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


@contextmanager
def profiler():
    p = Profiler(async_mode='disabled')
    with p:
        yield
    p.print(show_all=True)


@contextmanager
def timer(context=None):
    start = time.perf_counter()

    if context:
        with context:
            yield
    else:
        yield

    end = time.perf_counter()
    dt = end - start

    print(f"Spent : {dt:0.4f}")


with timer(profiler()):
    app = OdooApplication()

    overlays = [
        OdooVersionedString("odoo_tools_openapi._odoo.v{version_info[0]}"),
        "odoo_tools_openapi._odoo.common",
    ]

    app.add_plugin(OverlayModulePlugin("/home/llacroix/work2/odoo/odoo", overlays))
    app.add_plugin(AddonsPathPlugin(["/home/llacroix/work2/odoo/addons"]))
    app.add_plugin(InitOdooPlugin('test_aws'))
    app.add_plugin(OdooWSGIHandler())
    app.add_plugin(SessionStorePlugin())
    app.add_plugin(DbRoutePlugin())
    # app.add_plugin(BaseOdooApp())
    # app.add_plugin(LoggingPlugin(FileLogPlugin(Path.cwd() / 'mylog.txt')))
    app.add_plugin(LoggingPlugin())

    app.load()

    # import pdb; pdb.set_trace()

    app = app.application
