from django.contrib import admin
from spectools.models import *

class SiteOptionsAdmin(admin.ModelAdmin):
    model = SiteOptions

class XMLSchemaAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ['name']}

class XMLAttributeInline(admin.TabularInline):
    model = XMLAttribute
    exclude = ('attribute_group',)
    extra = 0

class XMLAttributeGroupAttributeInline(admin.TabularInline):
    model = XMLAttribute
    exclude = ('element',)
    extra = 0

class ChildElementsInline(admin.TabularInline):
    model = XMLRelationship
    extra = 0
    fk_name = 'parent'

class JSONChildElementsInline(admin.TabularInline):
    model = JSONObjectRelationship
    extra = 0
    fk_name = 'parent'

class JSONEnumsInline(admin.TabularInline):
    model = JSONObjectEnum
    extra = 0
    fk_name = 'parent'

class ElementConceptInline(admin.TabularInline):
    model = ElementConcept
    extra = 0

class XMLElementAdmin(admin.ModelAdmin):
    inlines = [XMLAttributeInline, ChildElementsInline, ElementConceptInline]
    list_display = ['name', 'slug', 'is_featured']
    ordering = ['name']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ['name']}
    radio_fields = {'children_type': admin.HORIZONTAL}
    filter_horizontal = ['attribute_groups']

class XMLAttributeGroupAdmin(admin.ModelAdmin):
    inlines = [XMLAttributeGroupAttributeInline]
    list_display = ['name']
    ordering = ['name']
    filter_horizontal = ['child_groups']

class DataTypeOptionInline(admin.TabularInline):
    model = DataTypeOption
    extra = 0

class DataTypeAdmin(admin.ModelAdmin):
    inlines = [DataTypeOptionInline]
    prepopulated_fields = {'slug': ['name']}
    list_display = ['name', 'base_type', 'xsd_name', 'is_featured']
    ordering = ['name']

class JSONObjectAdmin(admin.ModelAdmin):
    inlines = [JSONChildElementsInline, JSONEnumsInline]
    list_display = ['name', 'slug', 'pretty_object_type']
    list_filter = ['object_type']
    ordering = ['name']
    search_fields = ['name', 'slug']

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
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ['name']}

class ConceptAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}
    list_display = ['name', 'is_featured']

class StaticPageCollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'url', 'schema', 'order']

class StaticPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'url', 'collection', 'order']

admin.site.register(SiteOptions, SiteOptionsAdmin)
admin.site.register(XMLSchema, XMLSchemaAdmin)
admin.site.register(XMLElement, XMLElementAdmin)
admin.site.register(XMLAttributeGroup, XMLAttributeGroupAdmin)
admin.site.register(DataType, DataTypeAdmin)
admin.site.register(JSONObject, JSONObjectAdmin)
admin.site.register(DocumentFormat, DocumentFormatAdmin)
admin.site.register(ExampleDocument, ExampleDocumentAdmin)
admin.site.register(Concept, ConceptAdmin)
admin.site.register(StaticPageCollection, StaticPageCollectionAdmin)
admin.site.register(StaticPage, StaticPageAdmin)
