from json import dumps

from django.core.management.base import BaseCommand

from poa.models import Block, Transaction, WaitingTransaction


class Command(BaseCommand):
    def handle(self, *args, **options):
        Block.objects.all().delete()
        WaitingTransaction.objects.all().delete()
        Transaction.objects.all().delete()
        block = Block(
            payload=dumps({
                'miners':
                    [
                        'MIGJAoGBAK4syOk/QM65Tf0w1s0T/sZlugqjVrwCZgfc9gutq0UpUKORDIOGTO5QB6FTnmOu3D0auPVJVd49kHBculSQ+Uwnv06x9LsgYSB2KSJZ1Wzhe2fy6OvdyiAz0DjYopAItHV7LLOymkNXJqJWWB8HmjBCqq7xl/1hg+HGuuQvuXJzAgMBAAE=',
                        'MIGJAoGBAKVSpedkdflGykzyJTgn1wasXDL2rUGOBBMpwzjh7NXXcI03/+yG/N+DirDC0uNV9CFtmTRYHncbwomxlZz96OhtgJSdqRbvBt/469cjV7pJPFUfl0rF9/67S0kPIFhsV/OUTZByKIGG6sh0dTmQH1BkTLFvAhQK+7jkEOc2PbX1AgMBAAE=',
                    ]
            })
        )
        block.set_hash()
        block.save()
        Transaction(
            receiver='MIGJAoGBAK4syOk/QM65Tf0w1s0T/sZlugqjVrwCZgfc9gutq0UpUKORDIOGTO5QB6FTnmOu3D0auPVJVd49kHBculSQ+Uwnv06x9LsgYSB2KSJZ1Wzhe2fy6OvdyiAz0DjYopAItHV7LLOymkNXJqJWWB8HmjBCqq7xl/1hg+HGuuQvuXJzAgMBAAE=',
            amount=1000,
            block=block
        ).save()
        Transaction(
            receiver='MIGJAoGBAKVSpedkdflGykzyJTgn1wasXDL2rUGOBBMpwzjh7NXXcI03/+yG/N+DirDC0uNV9CFtmTRYHncbwomxlZz96OhtgJSdqRbvBt/469cjV7pJPFUfl0rF9/67S0kPIFhsV/OUTZByKIGG6sh0dTmQH1BkTLFvAhQK+7jkEOc2PbX1AgMBAAE=',
            amount=1000,
            block=block
        ).save()
