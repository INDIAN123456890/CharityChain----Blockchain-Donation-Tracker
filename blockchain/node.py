from copy import deepcopy
from .chain import SimpleBlockchain
from .smart_contract import CharityContract

class Node:
    def __init__(self, node_id, blockchain: SimpleBlockchain):
        self.node_id = node_id
        self.blockchain = deepcopy(blockchain)
        self.peers = []
        self.contract = CharityContract()

    def connect_peer(self, peer_node):
        if peer_node not in self.peers and peer_node is not self:
            self.peers.append(peer_node)

    def broadcast_transaction(self, tx):
        try:
            self.contract.donate(tx.sender, tx.recipient, tx.amount)
        except Exception as e:
            raise ValueError(f"Smart contract rejected: {e}")

        # Normal blockchain transaction handling
        self.blockchain.add_transaction(tx)
        for p in self.peers:
            try:
                p.blockchain.add_transaction(tx)
                p.contract.donate(tx.sender, tx.recipient, tx.amount)  # sync contract state
            except Exception:
                pass

    def mine_and_broadcast(self, miner_address):
        block = self.blockchain.mine_block(miner_address)
        if block:
            for p in self.peers:
                if len(p.blockchain.chain) < len(self.blockchain.chain):
                    p.blockchain = deepcopy(self.blockchain)
                    p.contract = deepcopy(self.contract)   # sync contract state
        return block

def create_network(num_nodes=3, difficulty=3):
    base_chain = SimpleBlockchain(difficulty=difficulty)
    nodes = [Node(f"node_{i}", base_chain) for i in range(num_nodes)]
    for n in nodes:
        for m in nodes:
            if n != m:
                n.connect_peer(m)
    return nodes
