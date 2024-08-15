from lxml import etree
from spectools.models import *

XSD_NS = 'http://www.w3.org/2001/XMLSchema'
XSD_NS_PREFIX = 'xs:'

# Complex type 'name's for which we don't import the <description>.
# Technically this couples this importer to the MusicXML XSD.
IGNORED_ELEMENT_DESCRIPTIONS = {'empty'}

class XSDParseError(Exception):
    pass

simple_type_xpath = etree.XPath('x:simpleType[@name=$name]', namespaces={'x': XSD_NS})
complex_type_xpath = etree.XPath('x:complexType[@name=$name]', namespaces={'x': XSD_NS})
group_xpath = etree.XPath('x:group[@name=$name]', namespaces={'x': XSD_NS})
attribute_group_xpath = etree.XPath('x:attributeGroup[@name=$name]', namespaces={'x': XSD_NS})

class XSDParser:
    def __init__(self, schema_slug:str, filedata:bytes):
        try:
            self.schema = XMLSchema.objects.filter(slug=schema_slug)[0]
        except IndexError:
            raise ValueError(f'XML schema with slug "{schema_slug}" not found. Make sure to create it in your DB.')
        self.element_qs = XMLElement.objects.filter(schema=self.schema)
        self.data_type_qs = DataType.objects.filter(schema=self.schema)
        self.xml = etree.XML(
            filedata,
            etree.XMLParser(resolve_entities=False) # resolve_entities prevents XXE attacks.
        )
        self.next_anonymous_id = 1

    def get_available_element_slug(self, name):
        if not self.element_qs.filter(slug=name).exists():
            return name
        for i in range(2, 10):
            slug = f'{name}-{i}'
            if not self.element_qs.filter(slug=slug).exists():
                return slug
        raise AssertionError # Shouldn't get here.

    def get_available_element_name(self):
        result = f'anonymous-{self.next_anonymous_id}'
        self.next_anonymous_id += 1
        return result

    def parse(self):
        for el in self.xml.xpath('x:element', namespaces={'x': XSD_NS}):
            self.parse_element(el)

    def parse_element(self, el):
        "Parses <xs:element>"
        element_name = el.attrib['name']

        base_element = None
        content_data_type = None
        element_type = el.attrib.get('type', None)
        if element_type:
            if element_type.startswith(XSD_NS_PREFIX):
                content_data_type = self.get_or_create_data_type(element_type)
            elif complex_type_xpath(self.xml, name=element_type):
                base_element = self.get_or_create_complex_type(element_type)
            elif simple_type_xpath(self.xml, name=element_type):
                content_data_type = self.get_or_create_data_type(element_type)

        xml_element = None
        if content_data_type or base_element:
            try:
                xml_element = self.element_qs.filter(
                    name=element_name,
                    content_data_type=content_data_type,
                    base_element=base_element,
                )[0]
            except IndexError:
                pass
        if xml_element is None:
            xml_element = XMLElement.objects.create(
                name=element_name,
                slug=self.get_available_element_slug(element_name),
                schema=self.schema,
                base_element=base_element,
                is_abstract_element=False,
                is_root=el.attrib.get('final', '') == '#all',
                description=self.parse_annotation_documentation(el),
                content_data_type=content_data_type,
                is_featured=False,
            )
        self.parse_element_children(el, xml_element)
        return xml_element

    def parse_annotation_documentation(self, el):
        """
        Gets the string within <xs:annotation><xs:documentation>,
        or empty string if that doesn't exist.
        """
        if el.attrib.get('name', '') not in IGNORED_ELEMENT_DESCRIPTIONS:
            doc_el = el.find(f'{{{XSD_NS}}}annotation/{{{XSD_NS}}}documentation')
            if doc_el is not None:
                return doc_el.text
        return ''

    def parse_complex_type(self, el, xml_element=None):
        "Parses <xs:complexType>"
        if xml_element is None:
            element_name = el.attrib['name']
            xml_element = XMLElement.objects.create(
                name=element_name,
                slug=self.get_available_element_slug(f'complex-{element_name}'),
                schema=self.schema,
                base_element=None,
                is_abstract_element=True,
                is_root=False,
                description=self.parse_annotation_documentation(el),
                content_data_type=None,
                is_featured=False,
            )
        else:
            if not xml_element.description:
                xml_element.description = self.parse_annotation_documentation(el)
                xml_element.save(update_fields=['description'])
        self.parse_element_children(el, xml_element)

        extension_el = el.find(f'{{{XSD_NS}}}simpleContent/{{{XSD_NS}}}extension')
        if extension_el is not None and 'base' in extension_el.attrib:
            xml_element.content_data_type = self.get_or_create_data_type(extension_el.attrib['base'])
            xml_element.save(update_fields=['content_data_type'])
            self.parse_element_children(extension_el, xml_element)

        extension_el = el.find(f'{{{XSD_NS}}}complexContent/{{{XSD_NS}}}extension')
        if extension_el is not None and 'base' in extension_el.attrib:
            xml_element.base_element = self.get_or_create_complex_type(extension_el.attrib['base'])
            xml_element.save(update_fields=['base_element'])
            self.parse_element_children(extension_el, xml_element)

    def parse_element_children(self, el, xml_element):
        child_order = 0
        for sub_el in el:
            tag_name = sub_el.tag
            if tag_name == f'{{{XSD_NS}}}attribute':
                if 'name' not in sub_el.attrib:
                    print(f'Skipping <{el.tag}> attribute due to missing "name"')
                    continue # TODO: Handle <xs:attribute ref="xml:lang"/>.
                XMLAttribute.objects.create(
                    element=xml_element,
                    attribute_group=None,
                    name=sub_el.attrib['name'],
                    is_required=sub_el.attrib.get('use') == 'required',
                    description='',
                    data_type=self.get_or_create_data_type(sub_el.attrib['type']),
                )
            elif tag_name == f'{{{XSD_NS}}}attributeGroup':
                xml_element.attribute_groups.add(
                    self.get_or_create_attribute_group(sub_el.attrib['ref'])
                )
            elif tag_name in (f'{{{XSD_NS}}}choice', f'{{{XSD_NS}}}sequence'):
                child_name = self.get_available_element_name()
                if tag_name == f'{{{XSD_NS}}}choice':
                    children_type = XMLElement.CHILDREN_TYPE_CHOICE
                else:
                    children_type = XMLElement.CHILDREN_TYPE_SEQUENCE
                child_xml_element = XMLElement.objects.create(
                    name=child_name,
                    slug=child_name,
                    schema=self.schema,
                    base_element=None,
                    is_abstract_element=True,
                    is_root=False,
                    description='',
                    content_data_type=None,
                    is_featured=False,
                    children_type=children_type,
                )
                self.parse_element_children(sub_el, child_xml_element)
                XMLRelationship.objects.create(
                    parent=xml_element,
                    child=child_xml_element,
                    min_amount=self.parse_minmax_occurs(sub_el, True),
                    max_amount=self.parse_minmax_occurs(sub_el, False),
                    child_order=child_order,
                )
                child_order += 1
            elif tag_name == f'{{{XSD_NS}}}complexType':
                self.parse_complex_type(sub_el, xml_element)
            elif tag_name == f'{{{XSD_NS}}}element':
                child_xml_element = self.parse_element(sub_el)
                XMLRelationship.objects.create(
                    parent=xml_element,
                    child=child_xml_element,
                    min_amount=self.parse_minmax_occurs(sub_el, True),
                    max_amount=self.parse_minmax_occurs(sub_el, False),
                    child_order=child_order,
                )
                child_order += 1
            elif tag_name == f'{{{XSD_NS}}}group':
                group_xml_element = self.get_or_create_group(sub_el.attrib['ref'])
                XMLRelationship.objects.create(
                    parent=xml_element,
                    child=group_xml_element,
                    min_amount=self.parse_minmax_occurs(sub_el, True),
                    max_amount=self.parse_minmax_occurs(sub_el, False),
                    child_order=child_order,
                )
                child_order += 1

    def parse_minmax_occurs(self, el, is_min):
        att_name = 'minOccurs' if is_min else 'maxOccurs'
        val = el.attrib.get(att_name, '1')
        if val == 'unbounded':
            val = None
        elif val.isdigit():
            val = int(val)
        return val

    def parse_group(self, el):
        "Parses <xs:group>"
        group_name = el.attrib['name']
        xml_element = XMLElement.objects.create(
            name=group_name,
            slug=self.get_available_element_slug(f'group-{group_name}'),
            schema=self.schema,
            base_element=None,
            is_abstract_element=True,
            is_root=False,
            description=self.parse_annotation_documentation(el),
            content_data_type=None,
            is_featured=False,
        )
        self.parse_element_children(el, xml_element)
        return xml_element

    def parse_restriction(self, el, data_type):
        "Parses <xs:restriction>"
        for sub_el in el:
            tag_name = sub_el.tag
            if tag_name == f'{{{XSD_NS}}}enumeration':
                DataTypeOption.objects.create(
                    data_type=data_type,
                    value=sub_el.attrib['value'],
                    description='',
                )
            elif tag_name == f'{{{XSD_NS}}}minInclusive':
                data_type.min_value = sub_el.attrib['value']
                data_type.save(update_fields=['min_value'])
            elif tag_name == f'{{{XSD_NS}}}maxInclusive':
                data_type.max_value = sub_el.attrib['value']
                data_type.save(update_fields=['max_value'])
            elif tag_name == f'{{{XSD_NS}}}pattern':
                data_type.regex = sub_el.attrib['value']
                data_type.save(update_fields=['regex'])
            elif tag_name == f'{{{XSD_NS}}}minLength':
                data_type.min_length = sub_el.attrib['value']
                data_type.save(update_fields=['min_length'])
            else:
                print('Unhandled <restriction> subelement:', tag_name)

    def parse_simple_type(self, el):
        "Parses <xs:simpleType>"
        type_name = el.attrib['name']
        description = self.parse_annotation_documentation(el)

        restriction_el = el.find(f'{{{XSD_NS}}}restriction')
        if restriction_el is not None:
            base_type = self.get_or_create_data_type(restriction_el.attrib['base'])
            union_types = None
        else:
            # The <simpleType> had no <restriction> elements. Check for
            # <union> instead.
            base_type = None
            union_types = []
            union_el = el.find(f'{{{XSD_NS}}}union')
            if union_el is None:
                print(f'Skipping simpleType "{type_name}" because it doesn\'t contain <restriction> or <union>')
                return
            for member_type in union_el.attrib['memberTypes'].split():
                union_types.append(self.get_or_create_data_type(member_type))

        data_type = DataType.objects.create(
            name=type_name,
            slug=type_name,
            schema=self.schema,
            description=description,
            is_featured=False,
            xsd_name='',
            base_type=base_type,
            min_value='',
            max_value='',
            regex='',
            min_length=None,
        )
        if union_types:
            data_type.union_types.add(*union_types)
        if restriction_el is not None:
            self.parse_restriction(restriction_el, data_type)
        return data_type

    def parse_attribute_group(self, el):
        "Parses <xs:attributeGroup>"
        ag = XMLAttributeGroup.objects.create(
            name=el.attrib['name'],
            description=self.parse_annotation_documentation(el),
        )
        for sub_el in el:
            tag_name = sub_el.tag
            if tag_name == f'{{{XSD_NS}}}attribute':
                if 'name' not in sub_el.attrib:
                    print(f'Skipping <attributeGroup {ag.name}> attribute due to missing "name"')
                    continue # TODO: Handle <xs:attribute ref="xml:lang"/>.
                XMLAttribute.objects.create(
                    element=None,
                    attribute_group=ag,
                    name=sub_el.attrib['name'],
                    is_required=sub_el.attrib.get('use') == 'required',
                    description='',
                    data_type=self.get_or_create_data_type(sub_el.attrib['type']),
                )
            elif tag_name == f'{{{XSD_NS}}}attributeGroup':
                ag.child_groups.add(
                    self.get_or_create_attribute_group(sub_el.attrib['ref'])
                )
        return ag

    def get_or_create_data_type(self, name):
        is_builtin = name.startswith(XSD_NS_PREFIX)
        if is_builtin:
            xsd_name = name[len(XSD_NS_PREFIX):]
            data_type, was_created = DataType.objects.get_or_create(
                xsd_name=xsd_name,
                schema=self.schema,
                defaults={
                    'name': xsd_name,
                    'slug': f'xsd-{xsd_name}',
                    'description': f'See <a href="https://www.w3.org/TR/xmlschema-2/#{xsd_name}">definition in the W3C XML Schema standard</a>.',
                    'is_featured': False,
                    'base_type': None,
                    'min_value': '',
                    'max_value': '',
                    'regex': '',
                    'min_length': None,
                }
            )
        else:
            try:
                data_type = self.data_type_qs.filter(slug=name)[0]
            except IndexError:
                data_type = self.parse_simple_type(
                    simple_type_xpath(self.xml, name=name)[0]
                )
        return data_type

    def get_or_create_complex_type(self, name):
        slug = f'complex-{name}'
        try:
            ct = self.element_qs.filter(slug=slug)[0]
        except IndexError:
            ct = XMLElement.objects.create(
                name=name,
                slug=slug,
                schema=self.schema,
                base_element=None,
                is_abstract_element=True,
                is_root=False,
                description='',
                content_data_type=None,
                is_featured=False
            )
            self.parse_complex_type(
                complex_type_xpath(self.xml, name=name)[0],
                ct
            )
        return ct

    def get_or_create_group(self, name):
        try:
            group = self.element_qs.filter(slug=f'group-{name}')[0]
        except IndexError:
            group = self.parse_group(
                group_xpath(self.xml, name=name)[0]
            )
        return group

    def get_or_create_attribute_group(self, name):
        try:
            ag = XMLAttributeGroup.objects.filter(name=name)[0]
        except IndexError:
            ag = self.parse_attribute_group(
                attribute_group_xpath(self.xml, name=name)[0]
            )
        return ag

def import_xsd(schema_slug:str, filedata:bytes):
    parser = XSDParser(schema_slug, filedata)
    parser.parse()
