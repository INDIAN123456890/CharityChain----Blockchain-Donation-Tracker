import hashlib, time, json
from .wallet import verify_signature

class Transaction:
    def __init__(self, sender, recipient, amount, pubkey, signature, meta=None, timestamp=None):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.pubkey = pubkey
        self.signature = signature
        self.meta = meta or {}
        self.timestamp = timestamp or time.time()

    def to_dict(self):
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "pubkey": self.pubkey,
            "signature": self.signature,
            "meta": self.meta,
            "timestamp": self.timestamp
        }

    def hash(self):
        return hashlib.sha256(json.dumps(self.to_dict(), sort_keys=True).encode()).hexdigest()

    def is_valid(self):
        if self.sender == "SYSTEM":
            return True
        message = f"{self.sender}{self.recipient}{self.amount}{self.meta}{self.timestamp}"
        return verify_signature(self.pubkey, message, self.signature)
