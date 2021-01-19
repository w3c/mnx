from django.core.management.base import BaseCommand
from spec.utils.serialization import freeze

class Command(BaseCommand):
    help = 'Serializes the DB into a JSON file.'

    def add_arguments(self, parser):
        parser.add_argument('outfile', nargs=1)

    def handle(self, **options):
        freeze(options['outfile'][0])
