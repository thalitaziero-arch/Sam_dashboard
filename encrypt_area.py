#!/usr/bin/env python3
"""Encrypts the private My Area payload so the PIN actually protects it.

The private HTML never ships in the clear: it is AES-GCM encrypted with a key
derived from the PIN via PBKDF2-SHA256. The browser runs the same derivation
with Web Crypto, so only the correct PIN can decrypt it.

A 4-digit PIN is only 10,000 combinations, so the iteration count is set high
on purpose: each guess costs ~0.4s in a browser, putting a full sweep at
roughly an hour of dedicated effort rather than milliseconds. That is a real
speed bump, not military-grade secrecy — see README notes.
"""
import base64
import json
import os
import sys

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ITERATIONS = 600_000


def encrypt(plaintext: str, pin: str):
    salt = os.urandom(16)
    nonce = os.urandom(12)
    key = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITERATIONS
    ).derive(pin.encode())
    ct = AESGCM(key).encrypt(nonce, plaintext.encode(), None)
    b64 = base64.b64encode
    return {
        "salt": b64(salt).decode(),
        "nonce": b64(nonce).decode(),
        "data": b64(ct).decode(),
        "iter": ITERATIONS,
    }


if __name__ == "__main__":
    pt = sys.stdin.read()
    pin = sys.argv[1] if len(sys.argv) > 1 else "2109"
    print(json.dumps(encrypt(pt, pin)))
