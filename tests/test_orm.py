from odoo_tools_openapi.orm.model import ApiModel, PropertyLister, JsonSerializable, MetaModel, DataStore
from odoo_tools_openapi.orm.fields import String


def test_model_properties_empty():
    NewModel = type('NM1', (PropertyLister,), {})
    assert NewModel.properties == set()

    prop1 = String()
    prop2 = String()
    prop3 = String()
    prop4 = String()
    prop5 = String()

    props = {
        "a": prop1,
        "b": prop2
    }

    props2 = {
        "c": prop3,
        "d": prop4
    }

    NewModel2 = type('NM2', (PropertyLister,), props)
    props_res_2 = NewModel2.properties
    assert props_res_2 == {"a", "b"}

    NewModel3 = type('NM3', (NewModel2,), {})
    props_res_2 = NewModel3.properties
    assert props_res_2 == {"a", "b"}

    NewModel3 = type('NM3', (NewModel2,), {"c": prop3})
    props_res_2 = NewModel3.properties
    assert props_res_2 == {"a", "b", "c"}

    NM4 = type('NM2', (PropertyLister,), props)
    NM5 = type('NM2', (PropertyLister,), props2)
    NM6 = type('NM6', (NM4, NM5), {})
    NM7 = type('NM7', (NM4, NM5), {'e': prop5})
    NM8 = type('NM8', (NM6,), {'e': prop5})
    # Test new class inheriting non related classes
    assert NM6.properties == {'a', 'b', 'c', 'd'}
    # Test new class inheriting non related classes with out properties
    assert NM7.properties == {'a', 'b', 'c', 'd', 'e'}
    # Test new class inheriting a class without own properties
    # but inherited ones
    assert NM8.properties == {'a', 'b', 'c', 'd', 'e'}


def test_json_serializer_parse():
    prop1 = String()
    prop2 = String()

    props = {
        "a": prop1,
        "b": prop2,
        "_values": DataStore()
    }

    AB = type('AB', (JsonSerializable,), props)

    obj = AB.parse({})

    assert obj.a is None
    assert obj.b is None

    obj = AB.parse({"a": "aa", "b": "bb"})
    assert obj.a == "aa"
    assert obj.b == "bb"


def test_json_serializer_to_json():
    prop1 = String()
    prop2 = String()

    props = {
        "a": prop1,
        "b": prop2,
        "_values": DataStore()
    }

    AB = type('AB', (JsonSerializable,), props)

    obj = AB.parse({})
    assert obj.to_json() == {"a": None, "b": None}

    obj = AB.parse({"a": "aa", "b": "bb"})
    assert obj.to_json() == {"a": "aa", "b": "bb"}

    obj = AB.parse({"a": "aa"})
    assert obj.to_json() == {"a": "aa", "b": None}


class test_api_model():
    prop1 = String()
    prop2 = String()

    props = {
        "a": prop1,
        "b": prop2,
    }

    AB = type('AB', (ApiModel,), props)

    obj = AB.parse({})
    assert obj.a is None
    obj.a = "fun"
    assert obj.a == "fun"
    assert obj._values.get('a') == "fun"
    del obj.a
    assert hasattr(obj, 'a')
    assert obj.a == None
    assert obj._values.get('a') is None
