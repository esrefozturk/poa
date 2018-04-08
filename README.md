<h1>Proof of Authority Blockchain</h1>

<h2>Prerequisites</h2>

- Python
- Django

<h2>How to Start a Miner None</h2>

- `python manage.py init`
- `python manage.py runserver 0.0.0.0:8000`

<h2>API Endpoints</h2>

<h3>Get Block Count</h3>

- Method : `GET`

- Path : `/block_count/`

- Response : <block_count>

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
  
