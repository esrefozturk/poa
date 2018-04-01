from json import loads

import requests

from poa.models import Block, Transaction, WaitingTransaction, NewBlock
from serializers import BlockSerializer
from settings import PUB, PEERS

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


def create_newblock(newblock):
    try:
        block = Block.objects.get(hash=newblock.previous_hash)
    except:
        # TODO: check if not exists
        previous_newblock = find_previous_block(newblock)
        check_newblock(previous_newblock)

    # TODO: make sign check

    Block(
        index=newblock.index,
        payload=newblock.payload,
        sign=newblock.sign,
        previous_hash=newblock.previos_hash,
        hash=newblock.hash,
        miner=newblock.miner
    ).save()
    newblock.delete()


def check_newblock(newblock):
    try:
        Block.objects.get(hash=newblock.hash)
    except:
        create_newblock(newblock)
        return
    newblock.delete()
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
    for peer in PEERS:
        requests.post(peer + 'consensus/', data=BlockSerializer(block).data)


def mine(waitingtransactions):
    current_block = Block.objects.all().order_by('-index')[0]
    block = Block(
        index=current_block.index + 1,
        previous_hash=current_block.hash,
        miner=PUB,
        payload='I Mine Like I Hash'
    )
    block.sign = '1234'  # sign( block.hash , PRI , 'SHA-256' ).encode('hex')
    block.save()

    for i in waitingtransactions:
        Transaction(
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
