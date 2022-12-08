import json
import logging
import werkzeug

from odoo import http
from odoo.http import Response, JsonRequest as JR
from odoo.tools import date_utils


_logger = logging.getLogger(__name__)


class JsonRequest(JR):
    pass


class PlainJsonRequest(JR):

    def __init__(self, *args):
        super().__init__(*args)

        self.params = {}

        args = self.httprequest.args
        request = None

        # regular jsonrpc2
        request = self.httprequest.get_data().decode(self.httprequest.charset)

        # Read POST content or POST Form Data named "request"
        try:
            self.jsonrequest = json.loads(request)
        except ValueError:
            msg = 'Invalid JSON data: %r' % (request,)
            _logger.info('%s: %s', self.httprequest.path, msg)
            raise werkzeug.exceptions.BadRequest(msg)

    def _json_response(self, result=None, error=None):
        mime = 'application/json'
        body = json.dumps(result, default=date_utils.json_default)

        return Response(
            body, status=error and error.pop('http_status', 200) or 200,
            headers=[('Content-Type', mime), ('Content-Length', len(body))]
        )
