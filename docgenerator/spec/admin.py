from django.contrib import admin
from spec.models import *

class XMLAttributeInline(admin.TabularInline):
    model = XMLAttribute
    exclude = ('attribute_group',)
    extra = 0

class XMLAttributeGroupAttributeInline(admin.TabularInline):
    model = XMLAttribute
    exclude = ('element',)
    extra = 1

class ChildElementsInline(admin.TabularInline):
    model = XMLRelationship
    extra = 1
    fk_name = 'parent'

class ElementConceptInline(admin.TabularInline):
    model = ElementConcept
    extra = 0

class XMLElementAdmin(admin.ModelAdmin):
    inlines = [XMLAttributeInline, ChildElementsInline, ElementConceptInline]
    list_display = ['name', 'slug', 'is_featured']
    ordering = ['name']
    prepopulated_fields = {'slug': ['name']}
    filter_horizontal = ['attribute_groups']

class XMLAttributeGroupAdmin(admin.ModelAdmin):
    inlines = [XMLAttributeGroupAttributeInline]
    list_display = ['name']
    ordering = ['name']

class DataTypeOptionInline(admin.TabularInline):
    model = DataTypeOption
    extra = 0

class DataTypeAdmin(admin.ModelAdmin):
    inlines = [DataTypeOptionInline]
    prepopulated_fields = {'slug': ['name']}
    list_display = ['name', 'is_featured']
    ordering = ['name']

class DocumentFormatAdmin(admin.ModelAdmin):
    model = DocumentFormat
    list_display = ['name', 'slug']

class ExampleDocumentConceptInline(admin.TabularInline):
    model = ExampleDocumentConcept
    extra = 0

class ExampleDocumentComparisonInline(admin.TabularInline):
    model = ExampleDocumentComparison
    extra = 0

class ExampleDocumentAdmin(admin.ModelAdmin):
    inlines = [ExampleDocumentConceptInline, ExampleDocumentComparisonInline]
    list_display = ['name', 'slug', 'image_url', 'is_featured']
    prepopulated_fields = {'slug': ['name']}

class ConceptAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}
    list_display = ['name', 'is_featured']

admin.site.register(XMLElement, XMLElementAdmin)
admin.site.register(XMLAttributeGroup, XMLAttributeGroupAdmin)
admin.site.register(DataType, DataTypeAdmin)
admin.site.register(DocumentFormat, DocumentFormatAdmin)
admin.site.register(ExampleDocument, ExampleDocumentAdmin)
admin.site.register(Concept, ConceptAdmin)
