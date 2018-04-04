import hashlib as hasher
import threading

from django.db import models
from rsa import sign, PrivateKey, verify, PublicKey

from settings import PUB


class Block(models.Model):
    index = models.IntegerField(default=0)
    timestamp = models.FloatField()
    payload = models.CharField(max_length=1024, default='')
    sign = models.CharField(max_length=2048, default='')
    previous_hash = models.CharField(max_length=1024)
    hash = models.CharField(max_length=1024, default='')
    miner = models.CharField(max_length=1024, default='')

    def __unicode__(self):
        return '{i} {t} {h}'.format(
            i=self.index,
            t=self.timestamp,
            h=self.hash
        )

    def mine(self):
        self.miner = PUB
        sha = hasher.sha256()
        sha.update(str(self.index) +
                   str(self.timestamp) +
                   str(self.payload) +
                   str(self.previous_hash))
        self.hash = sha.hexdigest()

        with open('rsa.pri', 'r') as f:
            privatekey = PrivateKey.load_pkcs1(f.read())

        self.sign = sign(self.hash, privatekey, 'SHA-256').encode('hex')


class BaseTransaction(models.Model):
    timestamp = models.FloatField()
    sender = models.CharField(max_length=1024)
    receiver = models.CharField(max_length=1024)
    amount = models.PositiveIntegerField()
    hash = models.CharField(max_length=1024)
    sign = models.CharField(max_length=1024)

    def __unicode__(self):
        return '{s} {r} {a}'.format(
            s=self.sender,
            r=self.receiver,
            a=self.amount

        )


class Transaction(BaseTransaction):
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='transactions')


class WaitingTransaction(BaseTransaction):
    pass

    def validate(self):
        from utils import calc_current_coin

        sha = hasher.sha256()
        sha.update(
            str(self.sender) +
            str(self.receiver) +
            str(self.amount) +
            str(self.timestamp)
        )
        hash = sha.hexdigest()

        if self.hash != hash:
            return False

        PUB = PublicKey.load_pkcs1(
            '''
            -----BEGIN RSA PUBLIC KEY-----
            {p}
            -----END RSA PUBLIC KEY-----
            '''.format(p='\n'.join([self.sender[i:i + 64] for i in range(0, len(self.sender), 64)]))
        )

        if not verify(hash, self.sign.decode('hex'), PUB):
            return False

        current_block = Block.objects.all().order_by('-index')[0]
        coin = calc_current_coin(self.sender, current_block)

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


from django.contrib import admin

admin.site.register(Block)
admin.site.register(Transaction)
admin.site.register(WaitingTransaction)
