try:
    from odoo.http import request, route, Controller
except ImportError:
    request = None
    Controller = type('Controller', (object,), {})

    def route(*args, **kwargs):
        def wrap(func):
            return func
        return wrap
