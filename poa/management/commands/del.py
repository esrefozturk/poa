from django.core.management.base import BaseCommand

from poa.models import Block, Transaction, WaitingTransaction


class Command(BaseCommand):
    def handle(self, *args, **options):
        Block.objects.all().delete()
        WaitingTransaction.objects.all().delete()
        Transaction.objects.all().delete()
