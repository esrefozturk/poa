from django.core.management.base import BaseCommand

from poa.models import Block, Transaction, WaitingTransaction, NewBlock


class Command(BaseCommand):
    def handle(self, *args, **options):
        Block.objects.all().delete()
        NewBlock.objects.all().delete()
        WaitingTransaction.objects.all().delete()
        Transaction.objects.all().delete()
        block = Block()
        block.save()
        Transaction(
            sender='',
            receiver='95344386748321127517311186835408940727299395407938192580718884751326195686720791344350837870274058813176963003318854548452770996534175351255491131768192086777382845454739005519379767540590689188817112826118114895319170267966855908325261377992665269559798602732004741648811835668513118239106142262092462954663',
            amount=1000,
            block=block
        ).save()
