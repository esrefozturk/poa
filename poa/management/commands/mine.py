from django.core.management.base import BaseCommand

from poa.utils import mine


class Command(BaseCommand):
    def handle(self, *args, **options):
        mine()
