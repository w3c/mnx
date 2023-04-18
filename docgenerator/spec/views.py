from django import http
from django.db.models import Q
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404, render
from spec.utils import htmlutils
from spec.models import *

def homepage(request):
    return render(request, 'homepage.html', {
        'schemas': XMLSchema.objects.order_by('name'),
        'featured_concepts': Concept.objects.filter(is_featured=True).order_by('name'),
        'static_pages': StaticPage.objects.select_related('collection').order_by('collection__order', 'order'),
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
        'child_relationships': element.get_child_relationships(),
        'parents': element.get_parent_elements(),
        'concepts': ElementConcept.objects.filter(element=element).select_related('concept'),
        'examples': ExampleDocumentElement.objects.filter(element=element).select_related('example').order_by(Lower('example__name')),
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

def json_object_list(request, schema_slug):
    schema = get_object_or_404(XMLSchema, slug=schema_slug)
    objects = JSONObject.objects.select_related('schema').filter(
        schema=schema,
    ).exclude(
        Q(object_type=JSONObject.OBJECT_TYPE_ARRAY) | Q(object_type=JSONObject.OBJECT_TYPE_LITERAL_STRING)
    ).order_by('name')
    return render(request, 'json_object_list.html', {
        'schema': schema,
        'objects': objects,
    })

def json_object_detail(request, schema_slug, slug):
    json_object = get_object_or_404(
        JSONObject.objects.select_related('schema'),
        schema__slug=schema_slug,
        slug=slug
    )
    if not json_object.has_docs_page():
        raise http.Http404()
    return render(request, 'json_object_detail.html', {
        'object': json_object,
        'child_relationships': json_object.get_child_relationships(),
        'examples': ExampleDocumentObject.objects.filter(json_object=json_object).select_related('example').order_by(Lower('example__name')),
    })

def data_type_list(request, schema_slug):
    schema = get_object_or_404(XMLSchema, slug=schema_slug)
    return render(request, 'data_type_list.html', {
        'schema': schema,
        'data_types': DataType.objects.filter(schema=schema).order_by(Lower('name')),
    })

def data_type_detail(request, schema_slug, slug):
    data_type = get_object_or_404(
        DataType.objects.select_related('schema'),
        schema__slug=schema_slug,
        slug=slug
    )
    el_attributes = []
    for att in XMLAttribute.objects.filter(data_type=data_type):
        el_attributes.extend([{
            'element': el,
            'attribute': att,
        } for el in att.get_elements()])
    el_attributes.sort(key=lambda x: x['element'].name)

    elements = []
    for el in XMLElement.objects.filter(content_data_type=data_type):
        for abs_el in el.get_nonabstract_elements():
            elements.append(abs_el)

    return render(request, 'data_type_detail.html', {
        'data_type': data_type,
        'elements': list(sorted(elements, key=lambda el: el.name)),
        'element_attributes': el_attributes,
        'options': DataTypeOption.objects.filter(data_type=data_type).order_by('order', Lower('value')),
    })

def example_list(request, schema_slug):
    schema = get_object_or_404(XMLSchema, slug=schema_slug)
    return render(request, 'example_list.html', {
        'schema': schema,
        'examples': ExampleDocument.objects.filter(schema=schema).order_by(Lower('name')),
    })

def example_detail(request, schema_slug, slug):
    example = get_object_or_404(
        ExampleDocument.objects.select_related('schema'),
        schema__slug=schema_slug,
        slug=slug
    )
    return render(request, 'example_detail.html', {
        'example': example,
        'augmented_doc': htmlutils.get_augmented_example(request.path, example.schema, example.document, diffs_use_divs=False)[1],
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
    main_schema = XMLSchema.objects.get(id=1)
    comparisons = []
    for edc in ExampleDocumentComparison.objects.filter(doc_format=other_format).select_related('example').order_by('position'):
        highlight_diffs, doc_html = htmlutils.get_augmented_example(request.path, main_schema, edc.example.document, True)
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
