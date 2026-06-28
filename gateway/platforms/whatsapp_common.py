# -*- coding: utf-8 -*-
"""gateway/platforms/whatsapp_common.py — WhatsApp Ortak Yardimcilari.

Iki WhatsApp platformu (whatsapp.py, whatsapp_cloud.py) arasinda
paylasilan fonksiyonlar: mesaj_temizle, numara_dogrula, medya_yukle.
"""

import os
import re
import json
import logging

try:
    import requests
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

logger = logging.getLogger(__name__)


def mesaj_temizle(mesaj: str, max_uzunluk: int = 4096) -> str:
    """WhatsApp mesajini temizler ve kisaltir.

    - HTML/Markdown taglarini temizle
    - Asiri bosluklari sil
    - Maksimum uzunluga kisalt

    Args:
        mesaj: Ham mesaj metni
        max_uzunluk: Maksimum karakter sayisi (varsayilan: 4096)

    Returns:
        str: Temizlenmis mesaj
    """
    if not mesaj:
        return ""

    # HTML taglarini temizle
    temiz = re.sub(r"<[^>]+>", "", mesaj)
    # Markdown linklerini temizle [text](url) -> text
    temiz = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", temiz)
    # Birden fazla satir boslugunu teke indir
    temiz = re.sub(r"\n{3,}", "\n\n", temiz)
    # Bastaki ve sondaki bosluklari sil
    temiz = temiz.strip()

    # Maksimum uzunluga kisalt (son kelimeyi bolmeden)
    if len(temiz) > max_uzunluk:
        temiz = temiz[:max_uzunluk]
        # Son kelimeyi kirpmamaya calis
        son_bosluk = temiz.rfind(" ")
        if son_bosluk > max_uzunluk * 0.8:
            temiz = temiz[:son_bosluk]
        temiz += "..."

    return temiz


def numara_dogrula(numara: str) -> bool:
    """Telefon numarasinin gecerliligini dogrular.

    Desteklenen formatlar:
    - 905551234567 (Türkiye, basinda + yok)
    - +905551234567 (uluslararasi)
    - 00905551234567 (uluslararasi, 00 ile)

    Args:
        numara: Dogrulanacak telefon numarasi

    Returns:
        bool: Numara gecerli ise True
    """
    if not numara:
        return False

    # Tum bosluk, tire, parantezleri kaldir
    temiz = re.sub(r"[\s\-\(\)\.]", "", numara)

    # + veya 00 ile baslayabilir
    if temiz.startswith("+"):
        temiz = temiz[1:]
    elif temiz.startswith("00"):
        temiz = temiz[2:]

    # Sadece rakam kaldi mi?
    if not temiz.isdigit():
        return False

    # Minimum 10, maksimum 15 hane (ITU-T E.164)
    if len(temiz) < 10 or len(temiz) > 15:
        return False

    return True


def medya_yukle(dosya_yolu: str, token: str = None, phone_id: str = None) -> dict:
    """WhatsApp Cloud API'ye medya dosyasi yukler.

    Args:
        dosya_yolu: Yuklenecek dosyanin yolu
        token: WhatsApp access token (env'den okunur)
        phone_id: WhatsApp Phone Number ID (env'den okunur)

    Returns:
        dict: {"durum": "basarili", "media_id": "..."} veya hata
    """
    if not _REQUESTS_OK:
        return {"durum": "hata", "hata": "requests kutuphanesi yok."}

    if not os.path.isfile(dosya_yolu):
        return {"durum": "hata", "hata": f"Dosya bulunamadi: {dosya_yolu}"}

    token = token or os.environ.get("WHATSAPP_TOKEN", "")
    phone_id = phone_id or os.environ.get("WHATSAPP_PHONE_ID", "")

    if not token or not phone_id:
        return {"durum": "hata", "hata": "WHATSAPP_TOKEN/PHONE_ID ayarlanmamis."}

    try:
        with open(dosya_yolu, "rb") as f:
            r = requests.post(
                f"https://graph.facebook.com/v18.0/{phone_id}/media",
                files={"file": f},
                data={
                    "messaging_product": "whatsapp",
                    "type": "application/octet-stream",
                },
                headers={"Authorization": f"Bearer {token}"},
                timeout=30,
            )
        data = r.json()
        if r.status_code == 200 and data.get("id"):
            return {"durum": "basarili", "media_id": data["id"]}
        return {"durum": "hata", "hata": f"Yukleme hatasi {r.status_code}: {data}"}
    except Exception as e:
        return {"durum": "hata", "hata": str(e)}


def ping() -> bool:
    """Ortak modulun calistigini kontrol eder."""
    return True
