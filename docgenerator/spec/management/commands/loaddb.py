from django.core.management.base import BaseCommand
from spec.utils.serialization import thaw

class Command(BaseCommand):
    help = 'Deserializes the DB from a JSON file.'

    def add_arguments(self, parser):
        parser.add_argument('infile', nargs=1)

    def handle(self, **options):
        thaw(options['infile'][0])
