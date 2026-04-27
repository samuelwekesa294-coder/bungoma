from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
import time
from typing import List


@dataclass(frozen=True)
class Transaction:
    sender: str
    recipient: str
    amount: float
    timestamp: float

    @classmethod
    def create(cls, sender: str, recipient: str, amount: float) -> "Transaction":
        if amount <= 0:
            raise ValueError("Transaction amount must be greater than 0")
        return cls(sender=sender, recipient=recipient, amount=amount, timestamp=time.time())


@dataclass(frozen=True)
class Block:
    index: int
    timestamp: float
    transactions: List[Transaction]
    proof: int
    previous_hash: str

    def to_hashable_dict(self) -> dict:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [asdict(t) for t in self.transactions],
            "proof": self.proof,
            "previous_hash": self.previous_hash,
        }


class Blockchain:
    """Simple Proof-of-Work blockchain with signed-like transactions."""

    def __init__(self) -> None:
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.create_genesis_block()

    def create_genesis_block(self) -> None:
        genesis = Block(
            index=1,
            timestamp=time.time(),
            transactions=[],
            proof=100,
            previous_hash="1",
        )
        self.chain.append(genesis)

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    def create_transaction(self, sender: str, recipient: str, amount: float) -> int:
        tx = Transaction.create(sender, recipient, amount)
        self.pending_transactions.append(tx)
        return self.last_block.index + 1

    def mine_block(self, miner_address: str) -> Block:
        # Reward the miner.
        self.pending_transactions.append(
            Transaction.create(sender="NETWORK", recipient=miner_address, amount=1.0)
        )

        last_proof = self.last_block.proof
        proof = self.proof_of_work(last_proof)
        previous_hash = self.hash_block(self.last_block)

        block = Block(
            index=len(self.chain) + 1,
            timestamp=time.time(),
            transactions=list(self.pending_transactions),
            proof=proof,
            previous_hash=previous_hash,
        )
        self.pending_transactions.clear()
        self.chain.append(block)
        return block

    @staticmethod
    def proof_of_work(last_proof: int) -> int:
        proof = 0
        while not Blockchain.valid_proof(last_proof, proof):
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof: int, proof: int) -> bool:
        guess = f"{last_proof}{proof}".encode()
        guess_hash = sha256(guess).hexdigest()
        return guess_hash.startswith("0000")

    @staticmethod
    def hash_block(block: Block) -> str:
        block_string = json.dumps(block.to_hashable_dict(), sort_keys=True).encode()
        return sha256(block_string).hexdigest()

    def is_valid_chain(self, chain: List[Block] | None = None) -> bool:
        candidate = chain or self.chain
        if len(candidate) == 0:
            return False

        for i in range(1, len(candidate)):
            prev = candidate[i - 1]
            block = candidate[i]

            if block.previous_hash != self.hash_block(prev):
                return False

            if not self.valid_proof(prev.proof, block.proof):
                return False

        return True

    def balance_of(self, address: str) -> float:
        total = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if tx.recipient == address:
                    total += tx.amount
                if tx.sender == address:
                    total -= tx.amount
        return total

    def as_dict(self) -> dict:
        return {
            "chain": [b.to_hashable_dict() for b in self.chain],
            "length": len(self.chain),
            "pending_transactions": [asdict(t) for t in self.pending_transactions],
        }
