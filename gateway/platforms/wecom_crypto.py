# -*- coding: utf-8 -*-
"""gateway/platforms/wecom_crypto.py — WeCom Sifreleme Yardimcilari.

WeCom callback sifreleme protokolunu uygular:
PKCS7 padding, AES decrypt/encrypt, XML parse.
"""

import os
import json
import base64
import hashlib
import random
import string
import logging
from xml.etree import ElementTree as ET

try:
    from Crypto.Cipher import AES
    _CRYPTO_OK = True
except ImportError:
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        _CRYPTO_OK = "cryptography"
    except ImportError:
        _CRYPTO_OK = False

logger = logging.getLogger(__name__)


def pkcs7_pad(veri: bytes, blok_boyutu: int = 32) -> bytes:
    """PKCS7 padding uygular.

    Args:
        veri: Padding eklenecek veri
        blok_boyutu: Blok boyutu (WeCom icin 32)

    Returns:
        bytes: Padding eklenmis veri
    """
    pad_uzunlugu = blok_boyutu - (len(veri) % blok_boyutu)
    padding = bytes([pad_uzunlugu] * pad_uzunlugu)
    return veri + padding


def pkcs7_unpad(veri: bytes) -> bytes:
    """PKCS7 padding kaldirir.

    Args:
        veri: Padding iceren veri

    Returns:
        bytes: Padding kaldirilmis veri
    """
    pad_uzunlugu = veri[-1]
    if pad_uzunlugu < 1 or pad_uzunlugu > 32:
        raise ValueError("Gecersiz padding uzunlugu")
    # Padding dogrulama
    for i in range(pad_uzunlugu):
        if veri[-(i + 1)] != pad_uzunlugu:
            raise ValueError("Gecersiz padding")
    return veri[:-pad_uzunlugu]


def aes_decrypt(sifreli_veri: bytes, aes_key: bytes, iv: bytes = None) -> bytes:
    """AES CBC mod decrypt.

    Args:
        sifreli_veri: Sifrelenmis veri (base64 cozulmus)
        aes_key: AES anahtari (base64 cozulmus)
        iv: IV (None ise AES key'in ilk 16 byte'i kullanilir)

    Returns:
        bytes: Cozulmus veri
    """
    if iv is None:
        iv = aes_key[:16]

    if _CRYPTO_OK == "cryptography":
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        cozulmus = decryptor.update(sifreli_veri) + decryptor.finalize()
    elif _CRYPTO_OK:
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        cozulmus = cipher.decrypt(sifreli_veri)
    else:
        raise ImportError("pycryptodome veya cryptography kutuphanesi gerekli.")

    return pkcs7_unpad(cozulmus)


def aes_encrypt(veri: bytes, aes_key: bytes, iv: bytes = None) -> bytes:
    """AES CBC mod encrypt.

    Args:
        veri: Sifrelenecek veri
        aes_key: AES anahtari (base64 cozulmus)
        iv: IV (None ise AES key'in ilk 16 byte'i)

    Returns:
        bytes: Sifrelenmis veri
    """
    if iv is None:
        iv = aes_key[:16]

    padli_veri = pkcs7_pad(veri)

    if _CRYPTO_OK == "cryptography":
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        return encryptor.update(padli_veri) + encryptor.finalize()
    elif _CRYPTO_OK:
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        return cipher.encrypt(padli_veri)
    else:
        raise ImportError("pycryptodome veya cryptography kutuphanesi gerekli.")


def xml_parse(ham_xml: str) -> dict:
    """WeCom XML mesajini parse eder.

    Args:
        ham_xml: Ham XML string

    Returns:
        dict: Parse edilmis XML verisi
    """
    try:
        root = ET.fromstring(ham_xml)
        return {child.tag: child.text for child in root}
    except ET.ParseError as e:
        logger.error("XML parse hatasi: %s", e)
        return {}


def xml_build(veri: dict, kok_etiket: str = "xml") -> str:
    """Sozlukten XML olusturur.

    Args:
        veri: XML'e cevrilecek sozluk
        kok_etiket: XML kok etiketi

    Returns:
        str: XML string
    """
    root = ET.Element(kok_etiket)
    for anahtar, deger in veri.items():
        child = ET.SubElement(root, anahtar)
        child.text = str(deger)
    return ET.tostring(root, encoding="utf-8", method="xml").decode("utf-8")


def msg_encrypt(ham_metin: str, aes_key: bytes, alici_id: str) -> str:
    """WeCom mesaj sifreleme (EncryptMsg).

    Args:
        ham_metin: Sifrelenecek xml/metin
        aes_key: AES anahtari
        alici_id: Alici ID (corpid)

    Returns:
        str: Base64 sifrelenmis metin
    """
    # Random 16 byte
    rand = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    # msg_len (4 byte, network byte order)
    msg_len = len(ham_metin)
    # Birlestir: random + msg_len + msg + alici_id
    veri = rand.encode("utf-8")
    veri += msg_len.to_bytes(4, byteorder="big")
    veri += ham_metin.encode("utf-8")
    veri += alici_id.encode("utf-8")

    sifreli = aes_encrypt(veri, aes_key)
    return base64.b64encode(sifreli).decode("utf-8")


def msg_decrypt(sifreli_b64: str, aes_key: bytes) -> dict:
    """WeCom mesaj cozme (DecryptMsg).

    Args:
        sifreli_b64: Base64 sifrelenmis metin
        aes_key: AES anahtari

    Returns:
        dict: {"content": "...", "receive_id": "..."} veya hata
    """
    try:
        sifreli_veri = base64.b64decode(sifreli_b64)
        cozulmus = aes_decrypt(sifreli_veri, aes_key)

        # Parse: random(16) + msg_len(4) + msg + receive_id
        msg_len_bytes = cozulmus[16:20]
        msg_len = int.from_bytes(msg_len_bytes, byteorder="big")
        msg = cozulmus[20:20 + msg_len].decode("utf-8")
        receive_id = cozulmus[20 + msg_len:].decode("utf-8")

        return {"content": msg, "receive_id": receive_id}
    except Exception as e:
        return {"hata": str(e)}


def dogrulama_sifrele(plaintext: str, timestamp: str, nonce: str, token: str) -> str:
    """SHA1 dogrulama imzasi olusturur (msg_signature).

    Args:
        plaintext: Sifrelenmis metin
        timestamp: Zaman damgasi
        nonce: Rastgele sayi
        token: WeCom token

    Returns:
        str: SHA1 hash imzasi
    """
    sorted_list = sorted([token, timestamp, nonce, plaintext])
    joined = "".join(sorted_list)
    return hashlib.sha1(joined.encode("utf-8")).hexdigest()


def ping() -> bool:
    """Sifreleme modulunun calistigini kontrol eder."""
    return _CRYPTO_OK is not False
