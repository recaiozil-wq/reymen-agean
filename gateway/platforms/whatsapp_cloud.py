# -*- coding: utf-8 -*-
"""gateway/platforms/whatsapp_cloud.py — WhatsApp Cloud API (Meta).

Graph API v18 uzerinden WhatsApp mesajlari gonderir.
.env'den WHATSAPP_TOKEN ve WHATSAPP_PHONE_ID okur.
"""

import os
import json
import logging

try:
    import requests
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

logger = logging.getLogger(__name__)

_BASE_URL = "https://graph.facebook.com/v18.0"


def _token_al() -> str:
    token = os.environ.get("WHATSAPP_TOKEN", "")
    if token and not token.startswith("***"):
        return token
    return ""


def send_message(hedef: str, mesaj: str, **kwargs) -> dict:
    """WhatsApp Cloud API ile mesaj gonderir.

    Args:
        hedef: Telefon numarasi (uluslararasi format, orn: 905551234567)
        mesaj: Mesaj icerigi (metin veya JSON)

    Returns:
        dict: {"durum": "basarili", "mesaj_id": "..."} veya {"durum": "hata", ...}
    """
    if not _REQUESTS_OK:
        return {"durum": "hata", "hata": "requests kutuphanesi yok."}

    token = _token_al()
    if not token:
        return {"durum": "hata", "hata": "WHATSAPP_TOKEN ayarlanmamis."}

    phone_id = os.environ.get("WHATSAPP_PHONE_ID", "")
    if not phone_id:
        return {"durum": "hata", "hata": "WHATSAPP_PHONE_ID ayarlanmamis."}

    # Mesaj tipi: varsayilan text
    mesaj_tipi = kwargs.get("tip", "text")
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": hedef,
    }

    if mesaj_tipi == "text":
        payload["type"] = "text"
        payload["text"] = {"body": mesaj[:4096], "preview_url": kwargs.get("preview_url", False)}
    elif mesaj_tipi == "template":
        payload["type"] = "template"
        payload["template"] = {
            "name": kwargs.get("template_name", mesaj),
            "language": {"code": kwargs.get("dil", "tr")},
            "components": kwargs.get("components", []),
        }
    elif mesaj_tipi == "image":
        payload["type"] = "image"
        payload["image"] = {"link": mesaj, "caption": kwargs.get("caption", "")}
    elif mesaj_tipi == "document":
        payload["type"] = "document"
        payload["document"] = {"link": mesaj, "filename": kwargs.get("filename", "belge.pdf")}
    elif mesaj_tipi == "audio":
        payload["type"] = "audio"
        payload["audio"] = {"link": mesaj}
    else:
        payload["type"] = "text"
        payload["text"] = {"body": mesaj[:4096]}

    try:
        r = requests.post(
            f"{_BASE_URL}/{phone_id}/messages",
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            timeout=15,
        )
        data = r.json()
        if r.status_code == 200 and data.get("messages"):
            return {"durum": "basarili", "mesaj_id": data["messages"][0].get("id", "")}
        return {"durum": "hata", "hata": f"API hatasi {r.status_code}: {data}"}
    except Exception as e:
        return {"durum": "hata", "hata": str(e)}


def ping() -> bool:
    """WhatsApp Cloud API baglantisini kontrol eder."""
    token = _token_al()
    phone_id = os.environ.get("WHATSAPP_PHONE_ID", "")
    if not token or not phone_id:
        return False
    try:
        r = requests.get(
            f"{_BASE_URL}/{phone_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        return r.status_code == 200
    except Exception:
        return False
