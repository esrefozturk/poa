import hashlib as hasher
from time import time

import requests
from rsa import verify, PublicKey

from poa.models import Block, Transaction, WaitingTransaction
from serializers import BlockSerializer
from settings import MINERS

LIMIT = 1
from settings import MINER_REWARD, IP


def get_block_count():
    return Block.objects.all().order_by('-index')[0].index + 1


def find_block(hash):
    for miner in MINERS:
        if IP == miner:
            continue
        try:
            r = requests.get('http://{m}:8000/blocks/{h}'.format(m=miner, h=hash))
            if r.status_code == 200:
                return r.json()[0]
        except:
            pass
    return None


def create_block_from_hash(hash):
    try:
        Block.objects.get(hash=hash)
        return True
    except:
        data = find_block(hash)
        if not validate_block(data):
            return False
        if not create_block_from_hash(data['previous_hash']):
            return False
        create_block(data)
        return True


def create_block(block_data):
    block = Block(
        index=block_data['index'],
        payload=block_data['payload'],
        previous_hash=block_data['previous_hash'],
        timestamp=block_data['timestamp'],
        miner=block_data['miner'],
        hash=block_data['hash'],
        sign=block_data['sign'],
    )
    block.save()

    for transaction_data in block_data['transactions']:
        transaction = Transaction(
            block=block,
            timestamp=transaction_data['timestamp'],
            sender=transaction_data['sender'],
            receiver=transaction_data['receiver'],
            amount=transaction_data['amount'],
            hash=transaction_data['hash'],
            sign=transaction_data['sign'],
        )
        transaction.save()
    return True


def validate_block(data):
    sha = hasher.sha256()
    sha.update(str(data['index']) +
               str(data['timestamp']) +
               str(data['payload']) +
               str(data['previous_hash']))
    hash = sha.hexdigest()

    if hash != data['hash']:
        return False

    PUB = PublicKey.load_pkcs1(
        '''
        -----BEGIN RSA PUBLIC KEY-----
        {p}
        -----END RSA PUBLIC KEY-----
        '''.format(p='\n'.join([data['miner'][i:i + 64] for i in range(0, len(data['miner']), 64)]))
    )

    if not verify(hash, data['sign'].decode('hex'), PUB):
        return False

    # TODO: transaction verificaiton

    return True


def calc_current_coin(sender, current_block):
    coin = 0

    if current_block.miner == sender:
        coin += MINER_REWARD

    for i in current_block.transactions.all():
        if i.sender == sender:
            coin -= i.amount
        elif i.receiver == sender:
            coin += i.amount

    if current_block.previous_hash != '':
        prev_block = Block.objects.get(hash=current_block.previous_hash)
        coin += calc_current_coin(sender, prev_block)

    return coin


def check_waitingtransaction():
    if WaitingTransaction.objects.all().count() >= LIMIT:
        mine(WaitingTransaction.objects.all().order_by()[:LIMIT])


def broadcast_new_block(block):
    for miner in MINERS:
        if miner == IP:
            continue
        try:
            requests.post('http://{m}:8000/consensus/'.format(m=miner), data=BlockSerializer(block).data)
        except:
            pass


def mine(waitingtransactions):
    current_block = Block.objects.all().order_by('-index')[0]
    block = Block(
        index=current_block.index + 1,
        previous_hash=current_block.hash,
        payload='I Mine Like I Hash',
        timestamp=time()
    )
    block.mine()
    block.save()

    for i in waitingtransactions:
        Transaction(
            timestamp=i.timestamp,
            sender=i.sender,
            receiver=i.receiver,
            amount=i.amount,
            block=block,
            hash=i.hash,
            sign=i.sign
        ).save()
        i.delete()

    broadcast_new_block(block)
