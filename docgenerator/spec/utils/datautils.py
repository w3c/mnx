from spec.models import ExampleDocumentElement
import xml.sax

ELEMENTS_TO_IGNORE = {'metadiff'}

class ElementCollector(xml.sax.handler.ContentHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = set()

    def startElement(self, name, attrs):
        if name not in ELEMENTS_TO_IGNORE:
            self.result.add(name)

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
        if existing.element_name in seen_elements:
            seen_elements.remove(existing.element_name)
        else:
            existing.delete()
    for element_name in seen_elements:
        ExampleDocumentElement.objects.create(
            example=example,
            element_name=element_name,
        )
