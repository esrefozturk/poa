from datetime import datetime
from json import loads

import requests

from poa.models import Block, Transaction, WaitingTransaction
from serializers import BlockSerializer
from settings import MINERS

LIMIT = 1


def get_block_count():
    return Block.objects.all().order_by('-index')[0].index + 1


def find_previous_block(newblock):
    for peer in PEERS:
        r = requests.get(peer + 'blocks/' + newblock.previous_hash)
        if r.status_code == 200:
            data = loads(r.json())
            n = NewBlock(
                index=data['index'],
                payload=data['payload'],
                sign=data['sign'],
                previous_hash=data['previous_hash'],
                hash=data['hash'],
                miner=data['miner']
            )
            n.save()
            return n


def create_newblock(block_data):
    print block_data
    try:
        block = Block.objects.get(hash=block_data['previous_hash'])
    except:
        return
        # TODO: check if not exists
        # previous_newblock = find_previous_block(newblock)
        # check_newblock(previous_newblock)

    # TODO: make sign check
    # TODO: create transactions


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
            timestamp=transaction_data['timestamp'],
            sender=transaction_data['sender'],
            receiver=transaction_data['receiver'],
            amount=transaction_data['amount']
        )
        transaction.save()


def check_newblock(block_data):
    try:
        Block.objects.get(hash=block_data['hash'])
    except:
        create_newblock(block_data)
        return


def calc_current_coin(sender, current_block):
    coin = 0

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
    for peer in MINERS:
        requests.post(peer + 'consensus/', data=BlockSerializer(block).data)


def mine(waitingtransactions):
    current_block = Block.objects.all().order_by('-index')[0]
    block = Block(
        index=current_block.index + 1,
        previous_hash=current_block.hash,
        payload='I Mine Like I Hash',
        timestamp=datetime.now()
    )
    block.save()

    for i in waitingtransactions:
        Transaction(
            timestamp=i.timestamp,
            sender=i.sender,
            receiver=i.receiver,
            amount=i.amount,
            block=block
        ).save()
        i.delete()

    broadcast_new_block(block)


'''
    last_block = Block.objects.all().order_by('-index')[0]
    block = Block(
        index=last_block.index + 1,
        previous_hash=last_block.hash,
    )

    sha = hasher.sha256()

    sha.update(str(block.index) +
               str(block.timestamp) +
               str(block.previous_hash)

               )

    block.hash = sha.hexdigest()

    # TODO: add POA
    block.sign = block.hash

    Transaction(
        sender='network',
        receiver=ME,
        amount=100
    ).save()

    consensus()





def consensus():
    block_counts = {}
    m = 0
    master = None
    for i in MINERS:
        block_counts[i] = int(requests.get(i+'block_count').text)
        if m < block_counts[i]:
            m = block_counts[i]
            master = i

    reinit_db(master, m)


def mine(transactions):
    last_block = Block.objects.all().order_by('-index')[0]
    block = Block(
        index=last_block.index + 1,
        previous_hash=last_block.hash,
    )

    sha = hasher.sha256()

    sha.update(str(block.index) +
               str(block.timestamp) +
               str(block.previous_hash)

               )

    block.hash = sha.hexdigest()

    # TODO: add POA
    block.sign = block.hash

    Transaction(
        sender='network',
        receiver=ME,
        amount=100
    ).save()

    consensus()



'''
