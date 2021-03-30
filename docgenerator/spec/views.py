from django import http
from django.shortcuts import get_object_or_404, render
from spec.utils import htmlutils
from spec.models import *

def homepage(request):
    return render(request, 'homepage.html', {
        'schemas': XMLSchema.objects.order_by('name'),
        'featured_concepts': Concept.objects.filter(is_featured=True).order_by('name'),
    })

def reference_homepage(request, schema_slug):
    schema = get_object_or_404(XMLSchema, slug=schema_slug)
    return render(request, 'reference_homepage.html', {
        'schema': schema,
        'featured_data_types': DataType.objects.filter(is_featured=True).order_by('name'),
        'featured_examples': ExampleDocument.objects.filter(schema=schema, is_featured=True).order_by('name'),
        'featured_elements': XMLElement.objects.filter(schema=schema, is_featured=True).order_by('name'),
    })

def element_list(request, schema_slug):
    schema = get_object_or_404(XMLSchema, slug=schema_slug)
    return render(request, 'element_list.html', {
        'schema': schema,
        'elements': XMLElement.objects.select_related('schema').filter(schema=schema, is_abstract_element=False).order_by('name'),
    })

def element_detail(request, schema_slug, slug):
    element = get_object_or_404(
        XMLElement.objects.select_related('schema'),
        schema__slug=schema_slug,
        slug=slug,
        is_abstract_element=False
    )
    return render(request, 'element_detail.html', {
        'element': element,
        'content_data_type': element.get_content_data_type(),
        'attributes': element.get_attributes(),
        'children': element.get_child_elements(),
        'parents': element.get_parent_elements(),
        'concepts': ElementConcept.objects.filter(element=element).select_related('concept'),
        'examples': ExampleDocumentElement.objects.filter(element_name=element.name).select_related('example').order_by('example__name'),
    })

def element_tree(request, schema_slug):
    schema = get_object_or_404(XMLSchema, slug=schema_slug)
    try:
        # TODO: Support multiple possible roots, as in MusicXML.
        root_element = XMLElement.objects.select_related('schema').filter(
            schema=schema,
            is_root=True
        )[0]
    except IndexError:
        raise http.Http404("You'll need to mark at least one XML element as is_root=True via the admin.")
    return render(request, 'element_tree.html', {
        'schema': schema,
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
        'elements': XMLElement.objects.filter(is_abstract_element=False, content_data_type=data_type).order_by('name'),
        'element_attributes': el_attributes,
        'options': DataTypeOption.objects.filter(data_type=data_type).order_by('value'),
    })

def example_list(request, schema_slug):
    schema = get_object_or_404(XMLSchema, slug=schema_slug)
    return render(request, 'example_list.html', {
        'schema': schema,
        'examples': ExampleDocument.objects.filter(schema=schema).order_by('name'),
    })

def example_detail(request, schema_slug, slug):
    example = get_object_or_404(
        ExampleDocument.objects.select_related('schema'),
        schema__slug=schema_slug,
        slug=slug
    )
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

def static_page_or_collection_detail(request):
    try:
        spc = StaticPageCollection.objects.filter(url=request.path)[0]
    except IndexError:
        pass
    else:
        return static_collection_detail(request, spc)
    sp = get_object_or_404(StaticPage, url=request.path)
    return render(request, 'static_page.html', {
        'static_page': sp,
    })

def static_collection_detail(request, collection):
    static_pages = StaticPage.objects.filter(collection=collection).order_by('order')
    return render(request, 'static_page_collection.html', {
        'collection': collection,
        'static_pages': static_pages,
    })
