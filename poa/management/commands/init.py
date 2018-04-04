from time import time

from django.core.management.base import BaseCommand

from poa.models import Block, Transaction


class Command(BaseCommand):
    def handle(self, *args, **options):
        block = Block(
            timestamp=0,
            previous_hash=''
        )
        block.mine()
        block.miner = ''
        block.sign = ''
        block.save()
        Transaction(
            timestamp=time(),
            sender='',
            receiver='MIGJAoGBAK4syOk/QM65Tf0w1s0T/sZlugqjVrwCZgfc9gutq0UpUKORDIOGTO5QB6FTnmOu3D0auPVJVd49kHBculSQ+Uwnv06x9LsgYSB2KSJZ1Wzhe2fy6OvdyiAz0DjYopAItHV7LLOymkNXJqJWWB8HmjBCqq7xl/1hg+HGuuQvuXJzAgMBAAE=',
            amount=1000,
            block=block
        ).save()
        Transaction(
            timestamp=time(),
            sender='',
            receiver='MIGJAoGBAKVSpedkdflGykzyJTgn1wasXDL2rUGOBBMpwzjh7NXXcI03/+yG/N+DirDC0uNV9CFtmTRYHncbwomxlZz96OhtgJSdqRbvBt/469cjV7pJPFUfl0rF9/67S0kPIFhsV/OUTZByKIGG6sh0dTmQH1BkTLFvAhQK+7jkEOc2PbX1AgMBAAE=',
            amount=1000,
            block=block
        ).save()
