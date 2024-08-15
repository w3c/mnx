from spectools.models import XMLElement, JSONObject, ExampleDocumentElement, ExampleDocumentObject
import xml.sax
import json

ELEMENTS_TO_IGNORE = {'metadiff'}

class ElementCollector(xml.sax.handler.ContentHandler):
    def __init__(self, schema, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = schema
        self.result = set()
        self.element_stack = []

    def get_element_obj(self, name):
        xml_elements = XMLElement.objects.filter(schema=self.schema, name=name, is_abstract_element=False)
        if self.element_stack:
            if self.element_stack[-1]:
                filtered_elements = []
                for xml_element in xml_elements:
                    parents = [x.id for x in xml_element.get_parent_elements()]
                    if self.element_stack[-1] in parents:
                        filtered_elements.append(xml_element)
                xml_elements = filtered_elements
            else: # Previous element ID is None.
                xml_elements = []
        try:
            obj = xml_elements[0]
        except IndexError:
            obj = None
        return obj

    def startElement(self, name, attrs):
        if name not in ELEMENTS_TO_IGNORE:
            obj = self.get_element_obj(name)
            self.element_stack.append(obj.id if obj else None)
            if obj:
                self.result.add(obj)

    def endElement(self, name):
        if name not in ELEMENTS_TO_IGNORE:
            del self.element_stack[-1]

def update_example_elements(example):
    """
    Given an ExampleDocument, creates all necessary
    ExampleDocumentElement objects.

    Any existing ExampleDocumentElement objects are
    untouched -- except if they're no longer represented
    in the given ExampleDocument (in which case they're
    deleted).
    """
    if example.schema.is_json:
        update_example_elements_json(example)
    else:
        update_example_elements_xml(example)

def accumulate_used_json_objects(json_data, object_def):
    """
    Given JSON data and a JSONObject that describes what level of the
    document tree we're in, returns a set of all JSONObjects used
    within (recursively).
    """
    result = set()
    if object_def.is_array():
        child_object_defs = [c.child for c in object_def.get_child_relationships()]
        for child_obj in json_data:
            child_object_def = JSONObject.get_jsonobject_for_data(child_obj, child_object_defs)
            result.update(accumulate_used_json_objects(child_obj, child_object_def))
    else:
        result.add(object_def)
        for rel in object_def.get_child_relationships():
            if rel.child_key in json_data:
                result.update(accumulate_used_json_objects(json_data[rel.child_key], rel.child))
    return result

def update_example_elements_json(example):
    schema = example.schema
    root_object = JSONObject.objects.get(schema=schema, name=JSONObject.ROOT_OBJECT_NAME)
    example_doc = json.loads(example.document)
    seen_objects = accumulate_used_json_objects(example_doc, root_object)
    for existing in ExampleDocumentObject.objects.filter(example=example):
        if existing.json_object in seen_objects:
            seen_objects.remove(existing.json_object)
        else:
            existing.delete()
    for obj in seen_objects:
        ExampleDocumentObject.objects.create(
            example=example,
            json_object=obj,
        )

def update_example_elements_xml(example):
    reader = xml.sax.make_parser()
    handler = ElementCollector(example.schema)
    xml.sax.parseString(example.document, handler)

    # At this point, handler.result is a set of all
    # element names seen in the document.
    seen_elements = handler.result

    for existing in ExampleDocumentElement.objects.filter(example=example):
        if existing.element in seen_elements:
            seen_elements.remove(existing.element)
        else:
            existing.delete()
    for element in seen_elements:
        ExampleDocumentElement.objects.create(
            example=example,
            element=element,
            element_name='', # TODO: Remove this.
        )
