import hashlib, binascii
from ecdsa import SigningKey, VerifyingKey, SECP256k1

def generate_wallet():
    sk = SigningKey.generate(curve=SECP256k1)
    vk = sk.get_verifying_key()
    priv = binascii.hexlify(sk.to_string()).decode()
    pub = binascii.hexlify(vk.to_string()).decode()
    address = hashlib.sha256(pub.encode()).hexdigest()[:40]
    return {"private_key": priv, "public_key": pub, "address": address}

def sign_message(private_key_hex: str, message: str) -> str:
    sk = SigningKey.from_string(binascii.unhexlify(private_key_hex), curve=SECP256k1)
    sig = sk.sign(message.encode())
    return binascii.hexlify(sig).decode()

def verify_signature(public_key_hex: str, message: str, signature_hex: str) -> bool:
    try:
        vk = VerifyingKey.from_string(binascii.unhexlify(public_key_hex), curve=SECP256k1)
        return vk.verify(binascii.unhexlify(signature_hex), message.encode())
    except Exception:
        return False
