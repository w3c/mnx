from spec.models import *
from django.contrib.auth.models import User
from django.core import serializers
import datetime
import os

JSON_INDENT = 4
MODELS_TO_FREEZE = (
    User,
    DataType,
    DataTypeOption,
    Concept,
    DocumentFormat,
    XMLElement,
    XMLAttributeGroup,
    XMLAttribute,
    XMLRelationship,
    ExampleDocument,
    ExampleDocumentConcept,
    ExampleDocumentComparison,
    ExampleDocumentElement,
    ElementConcept
)

def all_model_objects():
    for ModelClass in MODELS_TO_FREEZE:
        for obj in ModelClass.objects.all():
            # Avoid spamming the diffs with people's last_login
            # or date_joined, which will differ across machines.
            # We just set them to hard-coded values.
            if ModelClass == User:
                obj.last_login = datetime.datetime(2021, 1, 19, tzinfo=datetime.timezone.utc)
                obj.date_joined = datetime.datetime(2021, 1, 19, tzinfo=datetime.timezone.utc)

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
