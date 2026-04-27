from blockchain.core import Blockchain


def test_genesis_block_exists():
    chain = Blockchain()
    assert len(chain.chain) == 1
    assert chain.last_block.previous_hash == "1"


def test_transaction_and_mining_flow():
    chain = Blockchain()
    next_block = chain.create_transaction("alice", "bob", 2.5)
    assert next_block == 2

    mined = chain.mine_block("miner-1")
    assert mined.index == 2
    assert len(mined.transactions) == 2
    assert chain.pending_transactions == []


def test_balances_after_mining():
    chain = Blockchain()
    chain.create_transaction("alice", "bob", 3)
    chain.mine_block("miner-x")

    assert chain.balance_of("alice") == -3
    assert chain.balance_of("bob") == 3
    assert chain.balance_of("miner-x") == 1


def test_chain_validation_detects_tamper():
    chain = Blockchain()
    chain.mine_block("miner")
    assert chain.is_valid_chain()

    tampered = chain.chain.copy()
    tampered_block = tampered[1]
    tampered[1] = tampered_block.__class__(
        index=tampered_block.index,
        timestamp=tampered_block.timestamp,
        transactions=tampered_block.transactions,
        proof=tampered_block.proof,
        previous_hash="bad-hash",
    )

    assert chain.is_valid_chain(tampered) is False
