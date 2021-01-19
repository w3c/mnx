from django.shortcuts import get_object_or_404, render
from spec.utils import htmlutils
from spec.models import XMLElement, XMLAttribute, XMLRelationship, DataType, ExampleDocument, Concept, ExampleDocumentConcept, ElementConcept

ROOT_ELEMENT_SLUG = 'mnx' # TODO: Put this in configuration.

def homepage(request):
    return render(request, 'homepage.html', {
        'featured_concepts': Concept.objects.filter(is_featured=True).order_by('name'),
        'featured_data_types': DataType.objects.filter(is_featured=True).order_by('name'),
        'featured_examples': ExampleDocument.objects.filter(is_featured=True).order_by('name'),
        'featured_elements': XMLElement.objects.filter(is_featured=True).order_by('name'),
    })

def element_list(request):
    return render(request, 'element_list.html', {
        'elements': XMLElement.objects.order_by('name'),
    })

def element_detail(request, slug):
    element = get_object_or_404(XMLElement, slug=slug)
    return render(request, 'element_detail.html', {
        'element': element,
        'attributes': element.xmlattribute_set.order_by('name'),
        'children': XMLRelationship.objects.filter(parent=element).select_related('child').order_by('child__name'),
        'parents': XMLRelationship.objects.filter(child=element).select_related('parent').order_by('parent__name'),
        'concepts': ElementConcept.objects.filter(element=element).select_related('concept'),
    })

def element_tree(request):
    root_element = get_object_or_404(XMLElement, slug=ROOT_ELEMENT_SLUG)
    return render(request, 'element_tree.html', {
        'tree_html': htmlutils.get_element_tree_html(request.path, root_element),
    })

def data_type_list(request):
    return render(request, 'data_type_list.html', {
        'data_types': DataType.objects.order_by('name'),
    })

def data_type_detail(request, slug):
    data_type = get_object_or_404(DataType, slug=slug)
    return render(request, 'data_type_detail.html', {
        'data_type': data_type,
        'attributes': XMLAttribute.objects.filter(data_type=data_type).select_related('element').order_by('element__name'),
    })

def example_list(request):
    return render(request, 'example_list.html', {
        'examples': ExampleDocument.objects.order_by('name'),
    })

def example_detail(request, slug):
    example = get_object_or_404(ExampleDocument, slug=slug)
    return render(request, 'example_detail.html', {
        'example': example,
        'augmented_doc': htmlutils.get_augmented_xml(request.path, example.document),
        'concepts': ExampleDocumentConcept.objects.filter(example=example).order_by('example__name'),
    })

def concept_list(request):
    return render(request, 'concept_list.html', {
        'concepts': Concept.objects.order_by('name'),
    })

def concept_detail(request, slug):
    concept = get_object_or_404(Concept, slug=slug)
    return render(request, 'concept_detail.html', {
        'concept': concept,
        'examples': ExampleDocumentConcept.objects.filter(concept=concept).select_related('example').order_by('example__name'),
        'elements': ElementConcept.objects.filter(concept=concept).select_related('element').order_by('element__name'),
    })
