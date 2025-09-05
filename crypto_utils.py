import json
import os
from typing import Tuple
from nacl.public import PrivateKey, PublicKey, Box
from nacl.encoding import Base64Encoder

PROFILE_DIR = os.path.join(os.path.expanduser("~"), ".mibiri")


def ensure_profile_dir() -> None:
    if not os.path.isdir(PROFILE_DIR):
        os.makedirs(PROFILE_DIR, exist_ok=True)


def generate_keypair() -> Tuple[bytes, bytes]:
    priv = PrivateKey.generate()
    pub = priv.public_key
    return bytes(priv), bytes(pub)


def save_profile(username: str, private_key: bytes, public_key: bytes) -> str:
    ensure_profile_dir()
    path = os.path.join(PROFILE_DIR, f"{username}.json")
    data = {
        "username": username,
        "private_key": Base64Encoder.encode(private_key).decode(),
        "public_key": Base64Encoder.encode(public_key).decode(),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def load_profile(username: str) -> Tuple[bytes, bytes]:
    path = os.path.join(PROFILE_DIR, f"{username}.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    priv = Base64Encoder.decode(data["private_key"].encode())
    pub = Base64Encoder.decode(data["public_key"].encode())
    return priv, pub


def encrypt_message(sender_private_key: bytes, recipient_public_key: bytes, plaintext: str) -> str:
    box = Box(PrivateKey(sender_private_key), PublicKey(recipient_public_key))
    cipher = box.encrypt(plaintext.encode(), encoder=Base64Encoder)
    return cipher.decode()


def decrypt_message(recipient_private_key: bytes, sender_public_key: bytes, ciphertext_b64: str) -> str:
    box = Box(PrivateKey(recipient_private_key), PublicKey(sender_public_key))
    plaintext = box.decrypt(ciphertext_b64.encode(), encoder=Base64Encoder)
    return plaintext.decode()
