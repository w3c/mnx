from spectools.models import *

# Each of these types is a native JSONSchema type and also exists as a
# JSONObject.slug.
NATIVE_TYPES = set(['boolean'])

def make_json_schema(schema_slug='mnx'):
    """
    Creates a JSON schema by looking at the JSONObject information
    in the database. The result is a Python data structure that, if
    serialized to JSON, is a correct JSON schema.
    """
    # First, add the root object.
    root_object = JSONObject.objects.filter(
        schema__slug=schema_slug,
        name=JSONObject.ROOT_OBJECT_NAME
    )[0]
    result = get_schema_for_db_object(root_object)
    result.update({
        '$schema': 'https://json-schema.org/draft/2020-12/schema',
        '$id': 'https://w3c.github.io/mnx/docs/mnx-schema.json',
        'title': 'MNX document',
        'description': 'An encoding of Common Western Music Notation.',
    })

    # Next, add any defs. We do this for any JSONObject that appears as
    # JSONRelationship.child more than once.
    defs = {}
    def_objects = JSONObject.objects.filter(schema__slug=schema_slug)
    for def_object in def_objects:
        if def_object.slug not in NATIVE_TYPES and JSONObjectRelationship.objects.filter(child=def_object).count() > 1:
            defs[def_object.slug] = get_schema_for_db_object(def_object, use_defs=False)
    if defs:
        result['$defs'] = defs

    return result

def get_schema_for_db_object(db_object, use_defs=True):
    """
    Given a JSONObject instance, returns its JSON schema definition
    as a Python dictionary.
    """
    if db_object.slug in NATIVE_TYPES:
        return {
            'type': db_object.slug
        }
    if use_defs and JSONObjectRelationship.objects.filter(child=db_object).count() > 1:
        return {
            '$ref': f'#/$defs/{db_object.slug}'
        }
    object_type = db_object.object_type
    if object_type == JSONObject.OBJECT_TYPE_DICT:
        props = dict([(childrel.child_key, get_schema_for_db_object(childrel.child)) for childrel in db_object.get_child_relationships()])
        required = [childrel.child_key for childrel in db_object.get_child_relationships() if childrel.is_required]
        result = {
            'type': 'object',
            'properties': props,
            'additionalProperties': False
        }
        if required:
            result['required'] = list(sorted(required))
        return result
    elif object_type == JSONObject.OBJECT_TYPE_ARRAY:
        childrels = db_object.get_child_relationships()
        if len(childrels) == 1:
            items = get_schema_for_db_object(childrels[0].child)
        else:
            items = {
                'anyOf': [get_schema_for_db_object(childrel.child) for childrel in childrels],
            }
        result = {
            'type': 'array',
            'items': items
        }
        return result
    elif object_type == JSONObject.OBJECT_TYPE_NUMBER:
        result = {
            'type': 'integer'
        }
        enums = JSONObjectEnum.objects.filter(parent=db_object)
        if enums:
            result['enum'] = [int(e.name) for e in enums]
        return result
    elif object_type == JSONObject.OBJECT_TYPE_BOOLEAN:
        return {
            'type': 'boolean'
        }
    elif object_type == JSONObject.OBJECT_TYPE_STRING:
        result = {
            'type': 'string'
        }
        enums = JSONObjectEnum.objects.filter(parent=db_object)
        if enums:
            result['enum'] = [e.name for e in enums]
        return result
    elif object_type == JSONObject.OBJECT_TYPE_LITERAL_STRING:
        return {
            'type': 'string',
            'const': db_object.description
        }
