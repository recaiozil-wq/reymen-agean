# -*- coding: utf-8 -*-
"""gateway/wecom_crypto.py — WeCom Sifreleme.

WeCom mesaj sifreleme/sifre cozme (AES-256-CBC).
"""

import base64
import hashlib
import json
from Crypto.Cipher import AES


def sifre_coz(encrypted: str, aes_key: str, appid: str) -> str:
    """WeCom sifrelenmis mesaji coz.

    Args:
        encrypted: Base64-encoded sifreli metin
        aes_key: AES anahtari (base64)
        appid: Uygulama ID'si

    Returns:
        Cozulmus metin veya hata
    """
    try:
        key = base64.b64decode(aes_key)
        data = base64.b64decode(encrypted)
        cipher = AES.new(key, AES.MODE_CBC, data[:16])
        decrypted = cipher.decrypt(data[16:])

        # PKCS7 padding kaldir
        pad = decrypted[-1]
        decrypted = decrypted[:-pad]

        # XML mesaji ayikla
        msg = decrypted[16:]  # Random 16 byte atla
        msg_len = int.from_bytes(msg[:4], "big")
        return msg[4:4 + msg_len].decode("utf-8")
    except Exception as e:
        return f"[WeComCrypto]: Hata: {e}"


def sifrele(metin: str, aes_key: str, appid: str) -> str:
    """Mesaji WeCom formatinda sifrele."""
    import os
    try:
        key = base64.b64decode(aes_key)
        rand = os.urandom(16)
        msg_len = len(metin).to_bytes(4, "big")
        raw = rand + msg_len + metin.encode("utf-8") + appid.encode("utf-8")

        # PKCS7 padding
        pad_len = 32 - (len(raw) % 32)
        raw += bytes([pad_len] * pad_len)

        iv = os.urandom(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted = iv + cipher.encrypt(raw)
        return base64.b64encode(encrypted).decode("utf-8")
    except Exception as e:
        return f"[WeComCrypto]: Hata: {e}"


if __name__ == "__main__":
    print("[WeComCrypto] Test icin aes_key gerekli.")
