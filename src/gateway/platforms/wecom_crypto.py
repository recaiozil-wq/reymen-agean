# -*- coding: utf-8 -*-
"""WeCom (Enterprise WeChat) message crypto — PKCS7, SHA1 signature, encrypt/decrypt."""

from __future__ import annotations

import base64
import hashlib
import os
import random
import string
import struct
from xml.etree import ElementTree


# ── Exceptions ──────────────────────────────────────────────────────────────


class WeComCryptoError(Exception):
    pass


class SignatureError(WeComCryptoError):
    pass


class DecryptError(WeComCryptoError):
    pass


class EncryptError(WeComCryptoError):
    pass


# ── PKCS7 ───────────────────────────────────────────────────────────────────


class PKCS7Encoder:
    block_size = 32

    @staticmethod
    def encode(data: bytes) -> bytes:
        pad_len = PKCS7Encoder.block_size - (len(data) % PKCS7Encoder.block_size)
        return data + bytes([pad_len] * pad_len)

    @staticmethod
    def decode(data: bytes) -> bytes:
        if not data:
            raise DecryptError("empty data")
        pad_len = data[-1]
        if pad_len < 1 or pad_len > PKCS7Encoder.block_size:
            raise DecryptError(f"invalid padding byte: {pad_len}")
        if pad_len > len(data):
            raise DecryptError("padding exceeds data length")
        if data[-pad_len:] != bytes([pad_len] * pad_len):
            raise DecryptError("malformed padding")
        return data[:-pad_len]


# ── SHA1 signature ──────────────────────────────────────────────────────────


def _sha1_signature(token: str, timestamp: str, nonce: str, encrypted: str) -> str:
    items = sorted([token, timestamp, nonce, encrypted])
    return hashlib.sha1("".join(items).encode()).hexdigest()


# ── WXBizMsgCrypt ───────────────────────────────────────────────────────────


class WXBizMsgCrypt:
    def __init__(self, token: str, encoding_aes_key: str, receive_id: str):
        if not token:
            raise ValueError("token is required")
        if not encoding_aes_key:
            raise ValueError("encoding_aes_key is required")
        if len(encoding_aes_key) != 43:
            raise ValueError(f"encoding_aes_key must be 43 chars, got {len(encoding_aes_key)}")
        if not receive_id:
            raise ValueError("receive_id is required")
        self.token = token
        self.receive_id = receive_id
        self.key = base64.b64decode(encoding_aes_key + "=")

    def encrypt(self, plaintext: str, nonce: str = "", timestamp: str = "") -> str:
        if not nonce:
            nonce = self._random_nonce()
        if not timestamp:
            timestamp = str(int(__import__("time").time()))

        plaintext_bytes = plaintext.encode("utf-8")
        random_bytes = os.urandom(16)
        len_bytes = struct.pack("!I", len(plaintext_bytes))
        full_data = random_bytes + len_bytes + plaintext_bytes + self.receive_id.encode()

        encrypted = PKCS7Encoder.encode(full_data)
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        iv = self.key[:16]
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        encrypted_bytes = encryptor.update(encrypted) + encryptor.finalize()
        encrypted_b64 = base64.b64encode(encrypted_bytes).decode()

        msg_signature = _sha1_signature(self.token, timestamp, nonce, encrypted_b64)

        return f"""<xml>
<Encrypt><![CDATA[{encrypted_b64}]]></Encrypt>
<MsgSignature><![CDATA[{msg_signature}]]></MsgSignature>
<TimeStamp>{timestamp}</TimeStamp>
<Nonce><![CDATA[{nonce}]]></Nonce>
</xml>"""

    def decrypt(self, msg_signature: str, timestamp: str, nonce: str, encrypted: str) -> str:
        expected_sig = _sha1_signature(self.token, timestamp, nonce, encrypted)
        if msg_signature != expected_sig:
            raise SignatureError("signature mismatch")

        try:
            encrypted_bytes = base64.b64decode(encrypted)
        except Exception:
            raise DecryptError("invalid base64")

        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        iv = self.key[:16]
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(encrypted_bytes) + decryptor.finalize()

        plaintext = PKCS7Encoder.decode(decrypted)
        len_bytes = plaintext[16:20]
        msg_len = struct.unpack("!I", len_bytes)[0]
        return plaintext[20:20 + msg_len].decode("utf-8")

    def verify_url(self, msg_signature: str, timestamp: str, nonce: str, echostr: str) -> str:
        return self.decrypt(msg_signature, timestamp, nonce, echostr)

    @staticmethod
    def _random_nonce(length: int = 10) -> str:
        chars = string.ascii_letters + string.digits
        return "".join(random.choices(chars, k=length))
