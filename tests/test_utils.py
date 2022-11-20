from odoo_tools_openapi.utils import map_type, iter_attrib


def test_map_type_known_type():
    assert map_type('integer') == 'int'


def test_map_type_unknown_type():
    assert map_type('foo') == 'foo'


def test_iter_attrib():
    my_obj = type('obj', (object,), {'a': 'a', 'b': 'b', 'c': None})
    obj = my_obj()

    found = set()

    for attr, val in iter_attrib(obj, ['a', 'b']):
        found.add((attr, val))

    assert found == {('a', 'a'), ('b', 'b')}

    found = set()

    for attr, val in iter_attrib(obj, ['a', 'b', 'c']):
        found.add((attr, val))

    assert found == {('a', 'a'), ('b', 'b')}
