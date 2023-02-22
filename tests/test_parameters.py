from odootools_openapi.objects import Parameters
from mock import MagicMock


def test_empty_parameters():
    api = MagicMock()
    params = Parameters(api)
    assert len(params.parameters) == 0
    assert params.to_json() == {}


def test_base_parameters():
    api = MagicMock()

    def deref(ref):
        ref = MagicMock()
        ref.extensions = {
            "model": "res.users"
        }
        return ref

    api.deref = deref

    p1 = MagicMock()
    p1.schema.type = 'string'
    p1.name = 'name'

    p2 = MagicMock()
    p2.name = 'id'
    p2.schema.type = 'integer'

    p3 = MagicMock()
    p3.name = "user_id"
    p3.extensions = {"model": {"$ref": "res/user"}}
    p3.schema.type = 'integer'

    params = Parameters(api, [
        p1, p2, p3
    ])

    assert params.to_json() == {
        "id": "<int:id>",
        "name": "<string:name>",
        "user_id": "<model('res.users'):user_id>"
    }
