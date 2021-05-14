from spec.models import XMLElement, ExampleDocumentElement
import xml.sax

ELEMENTS_TO_IGNORE = {'metadiff'}

class ElementCollector(xml.sax.handler.ContentHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = set()
        self.element_stack = []

    def get_element_obj(self, name):
        xml_elements = XMLElement.objects.filter(name=name, is_abstract_element=False)
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
    reader = xml.sax.make_parser()
    handler = ElementCollector()
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
