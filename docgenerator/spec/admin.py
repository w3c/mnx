from django.contrib import admin
from spec.models import XMLElement, XMLAttribute, XMLRelationship, DataType, ExampleDocument, Concept, ExampleDocumentConcept, ElementConcept

class XMLAttributeInline(admin.TabularInline):
    model = XMLAttribute
    extra = 0

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

class DataTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}
    list_display = ['name', 'is_featured']

class ExampleDocumentConceptInline(admin.TabularInline):
    model = ExampleDocumentConcept
    extra = 0

class ExampleDocumentAdmin(admin.ModelAdmin):
    inlines = [ExampleDocumentConceptInline]
    list_display = ['name', 'slug', 'image_url', 'is_featured']
    prepopulated_fields = {'slug': ['name']}

class ConceptAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}
    list_display = ['name', 'is_featured']

admin.site.register(XMLElement, XMLElementAdmin)
admin.site.register(DataType, DataTypeAdmin)
admin.site.register(ExampleDocument, ExampleDocumentAdmin)
admin.site.register(Concept, ConceptAdmin)
