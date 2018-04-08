<h1>Proof of Authority Blockchain</h1>

In this project, I implemented a toy cryptocurrency blockchain from scratch. Here is some details:

- IP adresses of miner nodes are defined in [miners.txt](miners.txt) file.
- Public keys(Addresses) of miners are defined in genesis block payload.
- Blocks and transactions are signed with RSA public key digital signature scheme.
- Account based transaction format is used.
- REST API is used to interact with the nodes.


<h2>Prerequisites</h2>

- Python
  - RSA
  - Django
  - Django Rest Framework


<h2>How to Start a Miner None</h2>

- Put `*/10 * * * * cd <project path> && /usr/bin/python manage.py mine`
- `python manage.py init`
- `python manage.py runserver 0.0.0.0:8000`

<h2>API Endpoints</h2>

<h3>Get Block Count</h3>

- Method : `GET`

- Path : `/block_count/`

- Response :

```
{
    "block_count": <block_count>
}
```

<h3>Get Single Block Data</h3>

- Method : `GET`

- Path : `/blocks/<block_hash>/`

- Response :

```
{
  "index": 1,
  "timestamp": <timestamp>,
  "sign": <sign>,
  "hash": <hash>,
  "previous_hash": <previous_hash>,
  "transactions": [<transaction_data>, <transaction_data>, ...],
  "payload": <payload>,
  "miner": <miner>
}
```

<h3>Get Single Transaction Data</h3>

- Method : `GET`

- Path : `/transactions/<transaction_hash>/`

- Response :

```
{
  "sender": <sender>,
  "receiver": <receiver>,
  "amount": <amount>,
  "hash": <hash>,
  "timestamp": <timestamp>,
  "sign": <sign>
}
```


<h3>Create New Transaction</h3>

- Method : `POST`

- Path : `/new_transaction/`

- Request :

```
{
  "sender": <sender>,
  "receiver": <receiver>,
  "amount": <amount>,
  "hash": <hash>,
  "timestamp": <timestamp>,
  "sign": <sign>
}
```
  

<h2>How to Initialize Wallet</h2>

- Create new public address and key pairs : `python wallet.py create_new_wallet`

<h2>How to Use Wallet</h2>

- Send coin : `python wallet.py <public_key_of_receiver> <amount>`
