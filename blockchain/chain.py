import json
from .transaction import Transaction
from .block import Block

class SimpleBlockchain:
    def __init__(self, difficulty=3):
        self.chain = []
        self.mempool = []
        self.difficulty = difficulty
        self.balances = {}
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_tx = Transaction("SYSTEM", "network", 0, "", "", {"note": "genesis"})
        block = Block(0, [genesis_tx], "0")
        self.chain.append(block)

    def add_transaction(self, tx: Transaction):
        if not tx.is_valid():
            raise ValueError("Invalid transaction")
        self.mempool.append(tx)

    def valid_proof(self, block):
        return block.hash().startswith("0" * self.difficulty)

    def mine_block(self, miner_address: str):
        if not self.mempool:
            return None
        txs_to_mine = self.mempool.copy()
        index = len(self.chain)
        prev_hash = self.chain[-1].hash()
        block = Block(index, txs_to_mine, prev_hash)
        while not self.valid_proof(block):
            block.nonce += 1
        # reward miner
        reward_tx = Transaction("SYSTEM", miner_address, 1.0, "", "", {"note": "reward"})
        block.transactions.append(reward_tx)
        self.chain.append(block)
        self.mempool.clear()
        self.recompute_balances()
        return block

    def recompute_balances(self):
        self.balances = {}
        for blk in self.chain:
            for tx in blk.transactions:
                if tx.sender != "SYSTEM":
                    self.balances[tx.sender] = self.balances.get(tx.sender, 0) - tx.amount
                self.balances[tx.recipient] = self.balances.get(tx.recipient, 0) + tx.amount

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            cur, prev = self.chain[i], self.chain[i - 1]
            if cur.previous_hash != prev.hash():
                return False
            if not self.valid_proof(cur):
                return False
            for tx in cur.transactions:
                if tx.sender != "SYSTEM" and not tx.is_valid():
                    return False
        return True

    def to_json(self):
        return json.dumps([b.to_dict() for b in self.chain], indent=2)
