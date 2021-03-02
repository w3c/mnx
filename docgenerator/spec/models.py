from django.db import models
from django.urls import reverse

class DataType(models.Model):
    name = models.CharField(max_length=80)
    slug = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        db_table = 'data_types'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('data_type_detail', args=(self.slug,))

class DataTypeOption(models.Model):
    data_type = models.ForeignKey(DataType, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'data_type_options'

class Concept(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
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
    name = models.CharField(max_length=80)
    slug = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    attribute_groups = models.ManyToManyField('XMLAttributeGroup', blank=True)

    class Meta:
        db_table = 'xml_elements'
        verbose_name = 'XML element'
        verbose_name_plural = 'XML elements'

    def __str__(self):
        return self.slug

    def get_absolute_url(self):
        return reverse('element_detail', args=(self.slug,))

    def name_with_brackets(self):
        return f'<{self.name}>'

    def get_child_elements(self):
        return XMLElement.objects.filter(child_rel__parent=self).order_by('child_rel__child__name')

class XMLAttributeGroup(models.Model):
    name = models.CharField(max_length=300, unique=True)

    class Meta:
        db_table = 'xml_attribute_groups'
        verbose_name = 'XML attribute group'
        verbose_name_plural = 'XML attribute groups'

    def __str__(self):
        return self.name

class XMLAttribute(models.Model):
    element = models.ForeignKey(XMLElement, on_delete=models.CASCADE, null=True)
    attribute_group = models.ForeignKey(XMLAttributeGroup, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=80)
    is_required = models.BooleanField()
    description = models.TextField(blank=True)
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

    class Meta:
        db_table = 'xml_relationships'

class ExampleDocument(models.Model):
    name = models.CharField(max_length=300)
    slug = models.CharField(max_length=100, unique=True)
    blurb = models.TextField(blank=True)
    document = models.TextField()
    image_url = models.CharField(max_length=300, blank=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        db_table = 'example_documents'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from spec.utils.datautils import update_example_elements
        update_example_elements(self)

    def get_absolute_url(self):
        return reverse('example_detail', args=(self.slug,))

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
