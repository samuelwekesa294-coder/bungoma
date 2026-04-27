from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

from blockchain.core import Blockchain


class BlockchainNode:
    def __init__(self) -> None:
        self.blockchain = Blockchain()

    def make_handler(self):
        node = self

        class Handler(BaseHTTPRequestHandler):
            def _read_json(self) -> dict[str, Any]:
                length = int(self.headers.get("Content-Length", "0"))
                if not length:
                    return {}
                raw = self.rfile.read(length)
                return json.loads(raw.decode())

            def _write_json(self, status: int, payload: dict[str, Any]) -> None:
                data = json.dumps(payload).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self) -> None:  # noqa: N802
                parsed = urlparse(self.path)

                if parsed.path == "/chain":
                    self._write_json(200, node.blockchain.as_dict())
                    return

                if parsed.path == "/mine":
                    miner = parse_qs(parsed.query).get("miner", ["anonymous"])[0]
                    block = node.blockchain.mine_block(miner)
                    self._write_json(200, {"message": "New block mined", "block": block.to_hashable_dict()})
                    return

                if parsed.path == "/balance":
                    addr = parse_qs(parsed.query).get("address", [None])[0]
                    if not addr:
                        self._write_json(400, {"error": "Missing query param: address"})
                        return
                    self._write_json(200, {"address": addr, "balance": node.blockchain.balance_of(addr)})
                    return

                self._write_json(404, {"error": "Not found"})

            def do_POST(self) -> None:  # noqa: N802
                if self.path != "/transactions/new":
                    self._write_json(404, {"error": "Not found"})
                    return

                payload = self._read_json()
                required = {"sender", "recipient", "amount"}
                if not required.issubset(payload.keys()):
                    self._write_json(400, {"error": "Missing fields", "required": sorted(required)})
                    return

                try:
                    next_block = node.blockchain.create_transaction(
                        sender=str(payload["sender"]),
                        recipient=str(payload["recipient"]),
                        amount=float(payload["amount"]),
                    )
                except ValueError as err:
                    self._write_json(400, {"error": str(err)})
                    return

                self._write_json(201, {"message": f"Transaction queued for block {next_block}"})

            def log_message(self, format: str, *args):
                return

        return Handler

    def serve(self, host: str, port: int) -> None:
        server = ThreadingHTTPServer((host, port), self.make_handler())
        print(f"Blockchain node listening on http://{host}:{port}")
        server.serve_forever()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a simple blockchain node")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    BlockchainNode().serve(args.host, args.port)


if __name__ == "__main__":
    main()
