from django.db import models
from django.urls import reverse

class SiteOptions(models.Model):
    # Singleton model that's used to store general metadata
    # about the documentation website.
    site_name = models.CharField(max_length=100)
    xml_format_name = models.CharField(max_length=100)
    sidebar_html = models.TextField(blank=True,
        help_text='Raw HTML to put into the left sidebar of each page.'
    )

    class Meta:
        db_table = 'site_options'
        verbose_name_plural = 'site options'

    def __str__(self):
        return self.site_name

class XMLSchema(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'xml_schemas'
        verbose_name = 'XML schema'
        verbose_name_plural = 'XML schemas'

    def __str__(self):
        return self.name

    def reference_url(self):
        return reverse('reference_homepage', args=(self.slug,))

    def data_types_url(self):
        return reverse('data_type_list', args=(self.slug,))

    def examples_url(self):
        return reverse('example_list', args=(self.slug,))

    def elements_url(self):
        return reverse('element_list', args=(self.slug,))

    def element_tree_url(self):
        return reverse('element_tree', args=(self.slug,))

class DataType(models.Model):
    name = models.CharField(max_length=80)
    slug = models.CharField(max_length=80, unique=True)
    schema = models.ForeignKey(XMLSchema, on_delete=models.CASCADE)
    description = models.TextField(blank=True,
        help_text='HTML tags are allowed here.'
    )
    is_featured = models.BooleanField(default=False)
    xsd_name = models.CharField(max_length=80, blank=True,
        verbose_name='XSD name',
        help_text='Use this field if this data type is a native XSD type such as string.'
    )
    base_type = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE, related_name='+')
    union_types = models.ManyToManyField('self', blank=True, related_name='+',
        help_text='If this data type is a union of multiple other types, list them here.'
    )
    min_value = models.CharField(max_length=10, blank=True)
    max_value = models.CharField(max_length=10, blank=True)
    regex = models.CharField(max_length=200, blank=True)
    min_length = models.IntegerField(null=True, blank=True,
        help_text='This can be used for string types.'
    )

    class Meta:
        db_table = 'data_types'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('data_type_detail', args=(self.schema.slug, self.slug,))

class DataTypeOption(models.Model):
    data_type = models.ForeignKey(DataType, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)
    description = models.TextField(blank=True,
        help_text='HTML tags are allowed here.'
    )
    order = models.SmallIntegerField(default=0)

    class Meta:
        db_table = 'data_type_options'

class Concept(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True,
        help_text='HTML tags are allowed here.'
    )
    is_featured = models.BooleanField(default=False)

    class Meta:
        db_table = 'concepts'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('concept_detail', args=(self.slug,))

class DocumentFormat(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'document_formats'

    def __str__(self):
        return self.name

    def comparison_url(self):
        return reverse('format_comparison_detail', args=(self.slug,))

class XMLElement(models.Model):
    CHILDREN_TYPE_UNORDERED = 1
    CHILDREN_TYPE_SEQUENCE = 2
    CHILDREN_TYPE_CHOICE = 3
    CHILDREN_TYPES = (
        (CHILDREN_TYPE_UNORDERED, 'Unordered'),
        (CHILDREN_TYPE_SEQUENCE, 'Sequence'),
        (CHILDREN_TYPE_CHOICE, 'Choice'),
    )

    name = models.CharField(max_length=80)
    slug = models.CharField(max_length=80)
    disambiguation = models.CharField(max_length=80, blank=True,
        help_text='This is displayed next to the element name in parentheses in order to disambiguate it. E.g., "timewise" for part elements.'
    )
    schema = models.ForeignKey(XMLSchema, on_delete=models.CASCADE, default=1)
    base_element = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    is_abstract_element = models.BooleanField(default=False)
    is_root = models.BooleanField(default=False,
        help_text='Check this only for the root element(s) in the schema.'
    )
    description = models.TextField(blank=True,
        help_text='HTML tags are allowed here.'
    )
    content_data_type = models.ForeignKey(DataType, null=True, blank=True, on_delete=models.SET_NULL)
    is_featured = models.BooleanField(default=False)
    children_type = models.SmallIntegerField(
        default=CHILDREN_TYPE_UNORDERED,
        choices=CHILDREN_TYPES,
        help_text='This specifies the requirement for child elements.'
    )
    attribute_groups = models.ManyToManyField('XMLAttributeGroup', blank=True)

    class Meta:
        db_table = 'xml_elements'
        verbose_name = 'XML element'
        verbose_name_plural = 'XML elements'
        unique_together = (
            ('schema', 'slug'),
        )

    def __str__(self):
        return self.slug

    def get_absolute_url(self):
        return reverse('element_detail', args=(self.schema.slug, self.slug,))

    def name_with_brackets(self):
        return f'<{self.name}>'

    def optional_disambiguation(self):
        if self.disambiguation:
            return f' ({self.disambiguation})'
        return ''

    def get_attributes(self):
        result = []
        for el in [self] + self.get_all_base_elements():
            result += list(el.xmlattribute_set.all())
            for att_group in el.attribute_groups.all():
                result.extend(att_group.get_attributes())
        result.sort(key=lambda x: (not(x.is_required), x.name))
        return result

    def get_content_data_type(self):
        if self.content_data_type:
            return self.content_data_type
        if self.base_element:
            return self.base_element.get_content_data_type()
        return None

    def get_nonabstract_elements(self):
        result = []
        if self.is_abstract_element:
            for el in XMLElement.objects.filter(base_element=self):
                result.extend(el.get_nonabstract_elements())
        else:
            result.append(self)
        return result

    def get_child_relationships(self):
        if self.base_element:
            return self.base_element.get_child_relationships()
        else:
            return list(XMLRelationship.objects.filter(parent=self).order_by('child_order'))

    def get_child_elements(self):
        result = []
        for child in XMLElement.objects.filter(child_rel__parent=self):
            if child.is_abstract_element:
                result.extend(child.get_child_elements())
            else:
                result.append(child)
        if self.base_element:
            result.extend(self.base_element.get_child_elements())
        return sorted(set(result), key=lambda el: el.name)

    def get_parent_elements(self):
        result = []
        for parent in XMLElement.objects.filter(parent_rel__child=self):
            if parent.is_abstract_element:
                result.extend(parent.get_parent_elements())
                for parent_subclass in XMLElement.objects.filter(base_element=parent):
                    if not parent_subclass.is_abstract_element:
                        result.append(parent_subclass)
            else:
                result.append(parent)
        return sorted(set(result), key=lambda el: el.name)

    def get_all_base_elements(self):
        result = []
        if self.base_element:
            result.append(self.base_element)
            result.extend(self.base_element.get_all_base_elements())
        return result

    def get_actual_parent_of_children(self):
        for child_el in self.get_child_elements():
            for child_parent in XMLElement.objects.filter(parent_rel__child=child_el):
                return child_parent
        return self

    def get_children_type_text(self):
        if self.children_type == XMLElement.CHILDREN_TYPE_CHOICE:
            for relationship in XMLRelationship.objects.filter(child=self):
                min_amount = relationship.min_amount
                max_amount = relationship.max_amount
                if min_amount == 0 and max_amount is None:
                    return 'Zero or more of the following'
                elif min_amount == 1 and max_amount is None:
                    return 'One or more of the following'
                elif min_amount == 1 and max_amount == 1:
                    return 'Exactly one of the following'
                elif min_amount == 0 and max_amount == 1:
                    return 'Zero or one of the following'
        elif self.children_type == XMLElement.CHILDREN_TYPE_SEQUENCE:
            for relationship in XMLRelationship.objects.filter(child=self):
                min_amount = relationship.min_amount
                if min_amount == 0:
                    return 'In this order (Optional)'
        return {
            XMLElement.CHILDREN_TYPE_UNORDERED: 'In any order',
            XMLElement.CHILDREN_TYPE_SEQUENCE: 'In this order',
            XMLElement.CHILDREN_TYPE_CHOICE: 'One of the following',
        }[self.children_type]

class XMLAttributeGroup(models.Model):
    name = models.CharField(max_length=300, unique=True)
    description = models.TextField(blank=True,
        help_text='This is not displayed publicly.'
    )
    child_groups = models.ManyToManyField('XMLAttributeGroup', blank=True)

    class Meta:
        db_table = 'xml_attribute_groups'
        verbose_name = 'XML attribute group'
        verbose_name_plural = 'XML attribute groups'

    def __str__(self):
        return self.name

    def get_attributes(self):
        result = list(XMLAttribute.objects.filter(attribute_group=self))
        for child_group in self.child_groups.all():
            result.extend(child_group.get_attributes())
        return result

class XMLAttribute(models.Model):
    element = models.ForeignKey(XMLElement, on_delete=models.CASCADE, null=True)
    attribute_group = models.ForeignKey(XMLAttributeGroup, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=80)
    is_required = models.BooleanField()
    description = models.TextField(blank=True,
        help_text='HTML tags are allowed here.'
    )
    data_type = models.ForeignKey(DataType, on_delete=models.PROTECT)

    class Meta:
        db_table = 'xml_attributes'
        verbose_name = 'XML attribute'
        verbose_name_plural = 'XML attributes'

    def __str__(self):
        return self.name

class XMLRelationship(models.Model):
    parent = models.ForeignKey(XMLElement, on_delete=models.CASCADE, related_name='parent_rel')
    child = models.ForeignKey(XMLElement, on_delete=models.CASCADE, related_name='child_rel')
    min_amount = models.IntegerField(null=True, blank=True)
    max_amount = models.IntegerField(null=True, blank=True)
    child_order = models.SmallIntegerField(default=0)

    class Meta:
        db_table = 'xml_relationships'
        verbose_name = 'XML relationship'
        verbose_name_plural = 'XML relationships'

    def pretty_amount(self):
        if self.parent.children_type == XMLElement.CHILDREN_TYPE_CHOICE:
            return ''
        min_amount = self.min_amount
        max_amount = self.max_amount
        if min_amount == 1 and max_amount == 1:
            return '(Required)'
        if min_amount == 0 and max_amount == 1:
            return '(Optional)'
        if min_amount == 0 and max_amount is None:
            return '(Zero or more times)'
        if min_amount == 1 and max_amount is None:
            return '(One or more times)'
        return f'({min_amount} to {max_amount} times)'

class ExampleDocument(models.Model):
    name = models.CharField(max_length=300)
    slug = models.CharField(max_length=100)
    schema = models.ForeignKey(XMLSchema, on_delete=models.CASCADE)
    blurb = models.TextField(blank=True)
    document = models.TextField()
    image_url = models.CharField(max_length=300, blank=True,
        help_text='Path to the image within the docgenerator/media directory, e.g., "/static/examples/test.jpg".'
    )
    is_featured = models.BooleanField(default=False)

    class Meta:
        db_table = 'example_documents'
        unique_together = (
            ('schema', 'slug'),
        )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from spec.utils.datautils import update_example_elements
        update_example_elements(self)

    def get_absolute_url(self):
        return reverse('example_detail', args=(self.schema.slug, self.slug,))

class ExampleDocumentConcept(models.Model):
    example = models.ForeignKey(ExampleDocument, on_delete=models.CASCADE)
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE)

    class Meta:
        db_table = 'example_concepts'

class ExampleDocumentComparison(models.Model):
    example = models.ForeignKey(ExampleDocument, on_delete=models.CASCADE)
    doc_format = models.ForeignKey(DocumentFormat, on_delete=models.CASCADE)
    preamble = models.TextField(blank=True)
    document = models.TextField()
    position = models.SmallIntegerField()

    class Meta:
        db_table = 'example_comparisons'

    def get_absolute_url(self):
        return self.doc_format.comparison_url() + f'#{self.example.slug}'

    def preamble_html(self):
        if self.preamble:
            return '\n'.join(f'<p class="examplenotes">{line}</p>' for line in self.preamble.split('\n') if line)
        return ''

class ExampleDocumentElement(models.Model):
    # This is a cache of each element used in each
    # ExampleDocument. It's updated via ExampleDocument.save().
    example = models.ForeignKey(ExampleDocument, on_delete=models.CASCADE)
    element_name = models.CharField(max_length=80)

    class Meta:
        db_table = 'example_elements'

class ElementConcept(models.Model):
    element = models.ForeignKey(XMLElement, on_delete=models.CASCADE)
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE)

    class Meta:
        db_table = 'element_concepts'

class StaticPageCollection(models.Model):
    title = models.CharField(max_length=255)
    url = models.CharField(max_length=150,
        help_text='Make sure it starts and ends with slashes.'
    )
    schema = models.ForeignKey(XMLSchema, null=True, blank=True, on_delete=models.SET_NULL)
    order = models.SmallIntegerField()

    class Meta:
        db_table = 'static_page_collections'

    def __str__(self):
        return self.title

class StaticPage(models.Model):
    title = models.CharField(max_length=255)
    url = models.CharField(max_length=150,
        help_text='Make sure it starts and ends with slashes.'
    )
    collection = models.ForeignKey(StaticPageCollection, on_delete=models.CASCADE)
    order = models.SmallIntegerField(help_text='This is the order of the page within the collection. Ordering is ascending.')
    content = models.TextField()

    class Meta:
        db_table = 'static_pages'

    def __str__(self):
        return self.title
