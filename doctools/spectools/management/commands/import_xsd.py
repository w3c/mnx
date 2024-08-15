from django.core.management.base import BaseCommand
from spectools.utils.xsd import import_xsd

class Command(BaseCommand):
    help = 'Imports the given XSD file.'

    def add_arguments(self, parser):
        parser.add_argument('schema', nargs=1)
        parser.add_argument('infile', nargs=1)

    def handle(self, **options):
        with open(options['infile'][0], 'rb') as fp:
            import_xsd(options['schema'][0], fp.read())
