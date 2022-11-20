from odoo_tools_openapi.orm.model import ApiModel, PropertyLister, JsonSerializable, MetaModel
from odoo_tools_openapi.orm.fields import String


def test_model_properties_empty():
    NewModel = type('NM1', (PropertyLister,), {})
    assert NewModel.properties == set()

    prop1 = String()
    prop2 = String()
    props = {
        "a": prop1,
        "b": prop2
    }
    NewModel2 = type('NM2', (PropertyLister,), props)
    props2 = NewModel2.properties
    assert props2 == {"a", "b"}

    NewModel3 = type('NM3', (NewModel2,), {})
    props2 = NewModel3.properties
    assert props2 == {"a", "b"}
