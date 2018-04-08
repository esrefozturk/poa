import hashlib as hasher
import threading

from django.db import models

from settings import PUB


class Block(models.Model):
    index = models.IntegerField(default=0)
    timestamp = models.FloatField(default=0)
    payload = models.CharField(max_length=1024, default='')
    sign = models.CharField(max_length=2048, default='')
    previous_hash = models.CharField(max_length=1024, default='')
    hash = models.CharField(max_length=1024, default='')
    miner = models.CharField(max_length=1024, default='')

    def __unicode__(self):
        return self.hash

    def set_miner(self):
        self.miner = PUB

    def set_hash(self):
        from utils import hash_block
        self.hash = hash_block(self)

    def set_sign(self):
        from utils import sign_block
        self.sign = sign_block(self)

    def mine(self):
        self.set_miner()
        self.set_hash()
        self.set_sign()


class BaseTransaction(models.Model):
    timestamp = models.FloatField(default=0)
    sender = models.CharField(max_length=1024, default='')
    receiver = models.CharField(max_length=1024, default='')
    amount = models.PositiveIntegerField(default=0)
    hash = models.CharField(max_length=1024, default='')
    sign = models.CharField(max_length=1024, default='')

    def __unicode__(self):
        return self.hash


class Transaction(BaseTransaction):
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='transactions')


class WaitingTransaction(BaseTransaction):
    def check_waitintransaction_exist(self):
        try:
            WaitingTransaction.objects.get(hash=self.hash)
            return False
        except:
            return True

    def check_transaction_exist(self):
        try:
            Transaction.objects.get(hash=self.hash)
            return False
        except:
            return True

    def validate(self):

        from utils import calc_current_coin

        if not self.check_waitintransaction_exist():
            return False

        if not self.check_transaction_exist():
            return False


        from utils import hash_transaction
        hash = hash_transaction(self)

        if self.hash != hash:
            return False

        from utils import verify_transaction
        if not verify_transaction(self):
            return False

        coin = calc_current_coin(self.sender)

        if self.amount > coin:
            return False

        return True

    def save(self, **kwargs):
        if not self.validate():
            return

        super(WaitingTransaction, self).save(**kwargs)

        from utils import transaction_arrived

        t = threading.Thread(target=transaction_arrived, args=(self,))
        t.start()


from django.contrib import admin

admin.site.register(Block)
admin.site.register(Transaction)
admin.site.register(WaitingTransaction)
