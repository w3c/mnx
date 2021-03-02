from django.shortcuts import get_object_or_404, render
from spec.utils import htmlutils
from spec.models import *

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
    attributes = list(element.xmlattribute_set.all())
    attributes += list(XMLAttribute.objects.filter(attribute_group__xmlelement=element))
    attributes.sort(key=lambda x: x.name)

    return render(request, 'element_detail.html', {
        'element': element,
        'attributes': attributes,
        'children': XMLRelationship.objects.filter(parent=element).select_related('child').order_by('child__name'),
        'parents': XMLRelationship.objects.filter(child=element).select_related('parent').order_by('parent__name'),
        'concepts': ElementConcept.objects.filter(element=element).select_related('concept'),
        'examples': ExampleDocumentElement.objects.filter(element_name=element.name).select_related('example').order_by('example__name'),
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
    el_attributes = []
    qs = XMLAttribute.objects.filter(data_type=data_type)
    for att in qs.filter(element__isnull=False):
        el_attributes.append({
            'element': att.element,
            'attribute': att,
        })
    for att in qs.filter(element__isnull=True):
        for el in XMLElement.objects.filter(attribute_groups__xmlattribute=att):
            el_attributes.append({
                'element': el,
                'attribute': att,
            })
    el_attributes.sort(key=lambda x: x['element'].name)

    return render(request, 'data_type_detail.html', {
        'data_type': data_type,
        'element_attributes': el_attributes,
        'options': DataTypeOption.objects.filter(data_type=data_type).order_by('value'),
    })

def example_list(request):
    return render(request, 'example_list.html', {
        'examples': ExampleDocument.objects.order_by('name'),
    })

def example_detail(request, slug):
    example = get_object_or_404(ExampleDocument, slug=slug)
    return render(request, 'example_detail.html', {
        'example': example,
        'augmented_doc': htmlutils.get_augmented_xml(request.path, example.document)[1],
        'concepts': ExampleDocumentConcept.objects.filter(example=example).order_by('example__name'),
        'comparisons': ExampleDocumentComparison.objects.filter(example=example).select_related('doc_format'),
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

def format_comparison_detail(request, slug):
    other_format = get_object_or_404(DocumentFormat, slug=slug)
    comparisons = []
    for edc in ExampleDocumentComparison.objects.filter(doc_format=other_format).select_related('example').order_by('position'):
        highlight_diffs, doc_html = htmlutils.get_augmented_xml(request.path, edc.example.document, True)
        comparisons.append({
            'example': edc.example,
            'preamble_html': edc.preamble_html(),
            'document_html': doc_html,
            'other_document_html': htmlutils.get_prettified_xml(edc.document),
            'highlight_diffs': highlight_diffs,
        })
    return render(request, 'format_comparison_detail.html', {
        'other_format': other_format,
        'comparisons': comparisons,
    })
