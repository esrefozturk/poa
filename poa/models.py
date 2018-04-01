import hashlib as hasher
import threading

from django.db import models


class NewBlock(models.Model):
    index = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    payload = models.CharField(max_length=1024, default='')
    sign = models.CharField(max_length=1024, default='')
    previous_hash = models.CharField(max_length=1024, default='')
    hash = models.CharField(max_length=1024, default='')
    miner = models.CharField(max_length=1024)

    def save(self, **kwargs):
        super(NewBlock, self).save(**kwargs)
        from utils import check_newblock
        t = threading.Thread(target=check_newblock, args=(self,))
        t.start()

    def __unicode__(self):
        return '{i} {p} {h}'.format(
            i=self.index,
            p=self.previous_hash,
            h=self.hash

        )


class Block(models.Model):
    index = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    payload = models.CharField(max_length=1024, default='')
    sign = models.CharField(max_length=1024, default='')
    previous_hash = models.CharField(max_length=1024, default='')
    hash = models.CharField(max_length=1024, default='')
    miner = models.CharField(max_length=1024)

    def save(self, **kwargs):
        sha = hasher.sha256()
        sha.update(str(self.index) +
                   str(self.timestamp) +
                   str(self.payload) +
                   str(self.miner) +
                   str(self.previous_hash))
        self.hash = sha.hexdigest()
        super(Block, self).save(**kwargs)

    def __unicode__(self):
        return '{i} {p} {h}'.format(
            i=self.index,
            p=self.previous_hash,
            h=self.hash

        )


class Transaction(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='transactions')
    sender = models.CharField(max_length=1024)
    receiver = models.CharField(max_length=1024)
    amount = models.PositiveIntegerField()
    hash = models.CharField(max_length=1024, default='')

    def save(self, **kwargs):
        sha = hasher.sha256()
        sha.update(str(self.sender) +
                   str(self.receiver) +
                   str(self.amount)
                   )
        self.hash = sha.hexdigest()
        super(Transaction, self).save(**kwargs)

    def __unicode__(self):
        return '{s} {r} {a}'.format(
            s=self.sender,
            r=self.receiver,
            a=self.amount

        )


class WaitingTransaction(models.Model):
    sender = models.CharField(max_length=1024)
    receiver = models.CharField(max_length=1024)
    amount = models.PositiveIntegerField()

    def validate(self):
        from utils import calc_current_coin
        current_block = Block.objects.all().order_by('-index')[0]
        coin = calc_current_coin(self.sender, current_block)

        print coin
        if self.amount > coin:
            return False
        return True

    def save(self, **kwargs):
        if not self.validate():
            return

        super(WaitingTransaction, self).save(**kwargs)

        from utils import check_waitingtransaction

        t = threading.Thread(target=check_waitingtransaction)
        t.start()

    def __unicode__(self):
        return '{s} {r} {a}'.format(
            s=self.sender,
            r=self.receiver,
            a=self.amount
        )


from django.contrib import admin

admin.site.register(Block)
admin.site.register(NewBlock)
admin.site.register(Transaction)
admin.site.register(WaitingTransaction)
