TYPE_MAP = {
    "integer": "int",
}


def map_type(type_name):
    if type_name in TYPE_MAP:
        return TYPE_MAP[type_name]
    return type_name




def iter_attrib(iterator, attributes):
    for attrib in attributes:
        route_obj = getattr(iterator, attrib)
        if route_obj:
            yield attrib, route_obj


def ext(obj, name, default=None):
    if name in obj.extensions:
        return obj.extensions[name]
    else:
        return default
