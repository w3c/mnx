from django.conf import settings
from django.core.management.base import BaseCommand
from django.test.client import Client
from django.urls import reverse
from spec.models import *
import os
import shutil

INDEX_FILE = 'index.html'

class SiteGenerator:
    def __init__(self, dirname:str, verbose=True):
        self.dirname = dirname
        self.verbose = verbose
        self.client = Client()
        if not os.path.exists(dirname):
            os.mkdir(dirname)

    def log(self, message):
        if self.verbose:
            print(message)

    def generate(self):
        self.copy_media_files()
        self.generate_view('homepage')

        self.generate_view('concept_list')
        for concept in Concept.objects.all():
            self.generate_url(concept.get_absolute_url())

        for doc_format in DocumentFormat.objects.all():
            self.generate_url(doc_format.comparison_url())

        for schema in XMLSchema.objects.all():
            self.generate_url(schema.reference_url())
            self.generate_url(schema.data_types_url())
            if schema.is_json:
                self.generate_url(schema.json_objects_url())
            for data_type in DataType.objects.filter(schema=schema):
                self.generate_url(data_type.get_absolute_url())

            self.generate_url(schema.elements_url())
            self.generate_url(schema.element_tree_url())
            for element in XMLElement.objects.filter(schema=schema, is_abstract_element=False):
                self.generate_url(element.get_absolute_url())

            self.generate_url(schema.examples_url())
            for example in ExampleDocument.objects.filter(schema=schema):
                self.generate_url(example.get_absolute_url())

        for obj in JSONObject.objects.all():
            if obj.has_docs_page():
                self.generate_url(obj.get_absolute_url())

        for spc in StaticPageCollection.objects.all():
            self.generate_url(spc.url)

        for static_page in StaticPage.objects.all():
            self.generate_url(static_page.url)

    def generate_view(self, view_name, *view_args):
        url = reverse(view_name, args=view_args)
        self.generate_url(url)

    def generate_url(self, url):
        html = self.client.get(url).content
        file_dir = os.path.join(self.dirname, url[1:])
        self.log(file_dir)
        os.makedirs(file_dir, exist_ok=True)
        with open(os.path.join(file_dir, INDEX_FILE), 'wb') as fp:
            fp.write(html)

    def copy_media_files(self):
        self.log('Media files')
        output_dir = os.path.join(self.dirname, settings.STATIC_URL[1:])
        for static_dir in settings.STATICFILES_DIRS:
            shutil.copytree(static_dir, output_dir, dirs_exist_ok=True)

class Command(BaseCommand):
    help = 'Generates the static site.'

    def add_arguments(self, parser):
        parser.add_argument('directory', nargs=1)

    def handle(self, **options):
        generator = SiteGenerator(options['directory'][0])
        generator.generate()
