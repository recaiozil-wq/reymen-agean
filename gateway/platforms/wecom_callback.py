# -*- coding: utf-8 -*-
"""gateway/platforms/wecom_callback.py — WeCom Callback/Webhook Isleyici.

Gelen mesajlari dogrulama ve yanitlama.
WeCom msg_signature dogrulamasini yapar.
"""

import os
import json
import logging
from xml.etree import ElementTree as ET

try:
    import requests
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

from . import wecom_crypto

logger = logging.getLogger(__name__)


def _get_config() -> dict:
    """WeCom callback konfigurasyonunu .env'den okur."""
    return {
        "token": os.environ.get("WECOM_CALLBACK_TOKEN", ""),
        "encoding_aes_key": os.environ.get("WECOM_ENCODING_AES_KEY", ""),
        "corp_id": os.environ.get("WECOM_CORP_ID", ""),
    }


def verify_url(msg_signature: str, timestamp: str, nonce: str, echostr: str) -> dict:
    """WeCom URL dogrulama (GET istegi callback).

    WeCom, callback URL'yi dogrulamak icin GET istegi gonderir.
    Bu fonksiyon msg_signature'i dogrular ve echostr'u cozer.

    Args:
        msg_signature: WeCom'un gonderdigi imza
        timestamp: Zaman damgasi
        nonce: Rastgele sayi
        echostr: Sifrelenmis dogrulama metni

    Returns:
        dict: {"durum": "basarili", "echostr": "...", ...} veya hata
    """
    config = _get_config()
    token = config["token"]
    encoding_aes_key = config["encoding_aes_key"]
    corp_id = config["corp_id"]

    if not token or not encoding_aes_key or not corp_id:
        return {"durum": "hata", "hata": "WeCom callback ayarlari eksik (WECOM_CALLBACK_TOKEN, WECOM_ENCODING_AES_KEY, WECOM_CORP_ID)."}

    try:
        # Imza dogrulama
        beklenen_imza = wecom_crypto.dogrulama_sifrele(echostr, timestamp, nonce, token)
        if beklenen_imza != msg_signature:
            return {"durum": "hata", "hata": f"Imza uyusmazligi: beklenen={beklenen_imza}, gelen={msg_signature}"}

        # AES key'i base64 decode et
        aes_key = wecom_crypto.base64.b64decode(encoding_aes_key + "=")

        # echostr'u coz
        cozulen = wecom_crypto.msg_decrypt(echostr, aes_key)
        if "hata" in cozulen:
            return {"durum": "hata", "hata": cozulen["hata"]}

        return {
            "durum": "basarili",
            "echostr": cozulen["content"],
            "receive_id": cozulen["receive_id"],
        }
    except Exception as e:
        return {"durum": "hata", "hata": str(e)}


def receive_message(govde: bytes, msg_signature: str, timestamp: str, nonce: str) -> dict:
    """WeCom callback mesajini alir, dogrular ve cozer.

    Args:
        govde: HTTP body (XML)
        msg_signature: WeCom msg_signature
        timestamp: Zaman damgasi
        nonce: Rastgele sayi

    Returns:
        dict: {"durum": "basarili", "mesaj": {...}} veya hata
    """
    config = _get_config()
    token = config["token"]
    encoding_aes_key = config["encoding_aes_key"]
    corp_id = config["corp_id"]

    if not token or not encoding_aes_key or not corp_id:
        return {"durum": "hata", "hata": "WeCom callback ayarlari eksik."}

    try:
        # XML parse
        ham_xml = govde.decode("utf-8") if isinstance(govde, bytes) else govde
        xml_veri = wecom_crypto.xml_parse(ham_xml)

        encrypt_node = xml_veri.get("Encrypt", "")
        if not encrypt_node:
            return {"durum": "hata", "hata": "XML'de Encrypt node bulunamadi."}

        # Imza dogrulama
        beklenen_imza = wecom_crypto.dogrulama_sifrele(encrypt_node, timestamp, nonce, token)
        if beklenen_imza != msg_signature:
            return {"durum": "hata", "hata": f"Imza uyusmazligi: beklenen={beklenen_imza}, gelen={msg_signature}"}

        # AES key
        aes_key_bytes = wecom_crypto.base64.b64decode(encoding_aes_key + "=") if not encoding_aes_key.endswith("=") else wecom_crypto.base64.b64decode(encoding_aes_key)

        # Coz
        cozulen = wecom_crypto.msg_decrypt(encrypt_node, aes_key_bytes)
        if "hata" in cozulen:
            return {"durum": "hata", "hata": cozulen["hata"]}

        # Cozulen icerigi XML parse et
        icerik_xml = wecom_crypto.xml_parse(cozulen["content"])

        return {
            "durum": "basarili",
            "mesaj": icerik_xml,
            "receive_id": cozulen["receive_id"],
        }
    except Exception as e:
        return {"durum": "hata", "hata": str(e)}


def send_message(hedef: str, mesaj: str, **kwargs) -> dict:
    """WeCom callback yaniti olusturur.

    Args:
        hedef: Kullanici ID'si
        mesaj: Yanit mesaji

    Returns:
        dict: {"durum": "basarili", "xml": "..."} veya hata
    """
    config = _get_config()
    encoding_aes_key = config["encoding_aes_key"]
    corp_id = config["corp_id"]

    if not encoding_aes_key or not corp_id:
        return {"durum": "hata", "hata": "WeCom callback ayarlari eksik."}

    try:
        # Yanit XML'i olustur
        yanit_xml = wecom_crypto.xml_build({
            "ToUserName": hedef,
            "FromUserName": corp_id,
            "CreateTime": str(kwargs.get("timestamp", "0")),
            "MsgType": "text",
            "Content": mesaj[:2000],
        })

        # AES key
        aes_key_bytes = wecom_crypto.base64.b64decode(encoding_aes_key + "=") if not encoding_aes_key.endswith("=") else wecom_crypto.base64.b64decode(encoding_aes_key)

        # Sifrele
        timestamp = kwargs.get("timestamp", "0")
        nonce = kwargs.get("nonce", "0")
        sifreli = wecom_crypto.msg_encrypt(yanit_xml, aes_key_bytes, corp_id)
        imza = wecom_crypto.dogrulama_sifrele(sifreli, timestamp, nonce, config["token"])

        # Cevap XML'i
        cevap = wecom_crypto.xml_build({
            "Encrypt": sifreli,
            "MsgSignature": imza,
            "TimeStamp": timestamp,
            "Nonce": nonce,
        })

        return {"durum": "basarili", "xml": cevap}
    except Exception as e:
        return {"durum": "hata", "hata": str(e)}


def ping() -> bool:
    """WeCom callback modulunun calistigini kontrol eder."""
    config = _get_config()
    return bool(config["token"] and config["encoding_aes_key"] and config["corp_id"])
