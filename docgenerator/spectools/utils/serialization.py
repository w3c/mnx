from spectools.models import *
from django.contrib.auth.models import User
from django.core import serializers
from django.db import models
import datetime
import os

JSON_INDENT = 4
MODELS_TO_FREEZE = (
    User,
    XMLSchema,
    SiteOptions,
    DataType,
    DataTypeOption,
    Concept,
    DocumentFormat,
    XMLElement,
    XMLAttributeGroup,
    XMLAttribute,
    XMLRelationship,
    JSONObject,
    JSONObjectRelationship,
    JSONObjectEnum,
    ExampleDocument,
    ExampleDocumentConcept,
    ExampleDocumentComparison,
    ExampleDocumentElement,
    ExampleDocumentObject,
    ElementConcept,
    StaticPageCollection,
    StaticPage
)

class MonkeypatchedTextField(models.TextField):
    """
    This monkeypatches TextField so that the Django serialization
    framework will serialize strings differently:

    * If a string contains a newline character, the string will
    be serialized as a list of strings (split on newlines).

    * If a string doesn't contain a newline character, it will be
    serialized as normal (just as a normal string).
    """
    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        if '\n' in value:
            return value.split('\n')
        return str(value)

    def to_python(self, value):
        if isinstance(value, list):
            return '\n'.join(value)
        return super().to_python(value)

def monkeypatch_model(ModelClass):
    """
    Monkeypatches the given Django model class to replace any TextField
    with our custom MonkeypatchedTextField.

    Run this on every model class before serializing or deserializing,
    in order to serialize every text-with-newlines string into a list.
    """
    for field in ModelClass._meta.fields:
        if field.__class__ == models.TextField:
            field.__class__ = MonkeypatchedTextField

def all_model_objects():
    for ModelClass in MODELS_TO_FREEZE:
        monkeypatch_model(ModelClass)
        for obj in ModelClass.objects.all():
            # Avoid spamming the diffs with people's last_login
            # or date_joined, which will differ across machines.
            # We just set them to hard-coded values.
            if ModelClass == User:
                obj.last_login = datetime.datetime(2021, 1, 19, tzinfo=datetime.timezone.utc)
                obj.date_joined = datetime.datetime(2021, 1, 19, tzinfo=datetime.timezone.utc)

            # Remove all Windows newline characters ('\r').
            for field in ModelClass._meta.fields:
                value = getattr(obj, field.name)
                if isinstance(value, str) and '\r' in value:
                    value = value.replace('\r', '')
                    setattr(obj, field.name, value)

            yield obj

def freeze(outfile:str):
    """
    Saves model data as JSON to the given file name.
    """
    with open(outfile, 'w') as fp:
        fp.write(
            serializers.serialize('json', all_model_objects(), indent=JSON_INDENT)
        )

def thaw(infile:str):
    """
    Clears the database and loads model data from the
    given file name (assumed to be in the format generated
    by freeze()).
    """
    # Clear existing data.
    for ModelClass in reversed(MODELS_TO_FREEZE):
        ModelClass.objects.all().delete()
        monkeypatch_model(ModelClass)

    # Import fresh data.
    could_not_import = []
    with open(infile, 'r') as fp:
        for obj in serializers.deserialize('json', fp.read()):
            try:
                obj.save()
            except Exception:
                # This can happen if there's a circular reference
                # to an object that hasn't yet been created.
                could_not_import.append(obj)
    for obj in could_not_import:
        obj.save()
