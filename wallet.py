import hashlib as hasher
import sys
from time import time

import requests
from rsa import newkeys, PrivateKey, sign

MINERS = open('miners.txt').read().strip().split('\n')


def create_new_wallet():
    pub, pri = newkeys(1024)
    with open('rsa.pub', 'w') as f:
        f.write(pub.save_pkcs1())
    with open('rsa.pri', 'w') as f:
        f.write(pri.save_pkcs1())


def main():
    command = sys.argv[1]
    if command == 'create_new_wallet':
        create_new_wallet()
        return

    PUB = ''.join(open('rsa.pub').read().split('\n')[1:4])

    receiver = command
    amount = sys.argv[2]
    timestamp = time()

    sha = hasher.sha256()
    sha.update(
        str(PUB) +
        str(receiver) +
        str(amount) +
        str(timestamp)
    )
    hash = sha.hexdigest()

    with open('rsa.pri', 'r') as f:
        PRI = PrivateKey.load_pkcs1(f.read())

    sig = sign(hash, PRI, 'SHA-256').encode('hex')

    for miner in MINERS:
        try:
            requests.post(
                'http://{ip}:8000/new_transaction/'.format(
                    ip=miner
                ),
                data={
                    'timestamp': timestamp,
                    'sender': PUB,
                    'receiver': receiver,
                    'amount': amount,
                    'hash': hash,
                    'sign': sig,
                }

            )
        except:
            pass


if __name__ == '__main__':
    main()
