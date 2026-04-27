# Bungoma Blockchain Platform

This repository now contains a lightweight blockchain platform written in Python.

## Features
- Proof-of-work blockchain (`0000` difficulty prefix).
- Transaction queue and mining reward.
- Chain integrity validation.
- Wallet balance calculation from on-chain transactions.
- HTTP node server with endpoints:
  - `GET /chain`
  - `POST /transactions/new`
  - `GET /mine?miner=<address>`
  - `GET /balance?address=<address>`

## Run
```bash
python -m blockchain.node --host 127.0.0.1 --port 8000
```

## Example API calls
```bash
curl -X POST http://127.0.0.1:8000/transactions/new \
  -H 'Content-Type: application/json' \
  -d '{"sender":"alice","recipient":"bob","amount":2.5}'

curl "http://127.0.0.1:8000/mine?miner=miner-1"
curl "http://127.0.0.1:8000/balance?address=bob"
```

## Test
```bash
pytest -q
```
