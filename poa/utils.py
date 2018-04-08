import hashlib as hasher
from json import loads
from time import time

import requests
from rsa import verify, PublicKey, PrivateKey, sign

from poa.models import Block, Transaction, WaitingTransaction
from serializers import BlockSerializer, WaitingTransactionSerializer
from settings import LIMIT
from settings import MINERS
from settings import MINER_REWARD, IP


def hash_str(s):
    sha = hasher.sha256()
    sha.update(s)
    return sha.hexdigest()


def hash_block(b):
    return hash_str(str(b.index) + str(b.timestamp) + str(b.payload) + str(b.previous_hash))


def hash_transaction(t):
    return hash_str(str(t.sender) + str(t.receiver) + str(t.amount) + str(t.timestamp))


def sign_block(b):
    with open('rsa.pri', 'r') as f:
        privatekey = PrivateKey.load_pkcs1(f.read())

    return sign(b.hash, privatekey, 'SHA-256').encode('hex')


def verify_transaction(t):
    PUB = PublicKey.load_pkcs1(
        '''
        -----BEGIN RSA PUBLIC KEY-----
        {p}
        -----END RSA PUBLIC KEY-----
        '''.format(p='\n'.join([t.sender[i:i + 64] for i in range(0, len(t.sender), 64)]))
    )

    if not verify(t.hash, t.sign.decode('hex'), PUB):
        return False
    return True


def get_newest_block():
    return Block.objects.all().order_by('-index', 'timestamp')[0]


def get_block_count():
    return get_newest_block().index + 1


def broadcast_new_transaction(waiting_transaction):
    for miner in MINERS:
        if miner == IP:
            continue
        try:
            requests.post(
                'http://{ip}:8000/new_transaction/'.format(
                    ip=miner
                ),
                data=WaitingTransactionSerializer(waiting_transaction).data
            )
        except:
            pass


def broadcast_new_block(block):
    for miner in MINERS:
        if miner == IP:
            continue
        try:
            requests.post('http://{m}:8000/consensus/'.format(m=miner), data=BlockSerializer(block).data)
        except:
            pass


def mine():
    waiting_transactions = WaitingTransaction.objects.all()[:LIMIT]

    if waiting_transactions.count() == 0:
        return

    newest_block = get_newest_block()
    block = Block(
        index=newest_block.index + 1,
        previous_hash=newest_block.hash,
        payload='Let"s sign it',
        timestamp=time()
    )
    block.mine()
    block.save()

    for i in waiting_transactions:
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


def transaction_arrived(waiting_transaction):
    broadcast_new_transaction(waiting_transaction)

    if WaitingTransaction.objects.all().count() >= LIMIT:
        mine()


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


def validate_transaction(transaction):
    sha = hasher.sha256()
    sha.update(str(transaction['sender']) +
               str(transaction['receiver']) +
               str(transaction['amount']) +
               str(transaction['timestamp']))
    hash = sha.hexdigest()

    if hash != transaction['hash']:
        return False

    PUB = PublicKey.load_pkcs1(
        '''
        -----BEGIN RSA PUBLIC KEY-----
        {p}
        -----END RSA PUBLIC KEY-----
        '''.format(p='\n'.join([transaction['sender'][i:i + 64] for i in range(0, len(transaction['sender']), 64)]))
    )

    if not verify(hash, transaction['sign'].decode('hex'), PUB):
        return False


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

    MINER_PUBS = loads(Block.objects.get(index=0).payload)['miners']
    if not data['miner'] in MINER_PUBS:
        return False

    for i in data['transactions']:
        validate_transaction(i)

    return True


def calc_current_coin_from_block(sender, block):
    coin = 0

    if block.miner == sender:
        coin += MINER_REWARD

    for i in block.transactions.all():
        if i.sender == sender:
            coin -= i.amount
        elif i.receiver == sender:
            coin += i.amount

    if block.index == 0:
        return coin
    else:
        return coin + calc_current_coin_from_block(sender, Block.objects.get(hash=block.previous_hash))


def calc_current_coin(sender):
    newest_block = get_newest_block()

    coin = calc_current_coin_from_block(sender, newest_block)
    for w in WaitingTransaction.objects.all():
        if w.sender == sender:
            coin -= w.amount

    return coin
