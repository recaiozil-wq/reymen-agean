# -*- coding: utf-8 -*-
"""gateway/platforms/whatsapp.py — WhatsApp Platformu.

WhatsApp Business API veya webhook uzerinden mesaj gonderir.
"""

import os
import requests


def _token_al() -> str:
    token = os.environ.get("WHATSAPP_TOKEN", "")
    if token and not token.startswith("***"):
        return token
    return ""


def baslat():
    pass


def durdur():
    pass


def mesaj_gonder(hedef: str, mesaj: str) -> str:
    """WhatsApp'a mesaj gonder.

    Args:
        hedef: Telefon numarasi (uluslararasi, +90xxxxxxxxx)
        mesaj: Gonderilecek metin
    """
    token = _token_al()
    if not token:
        return "[WhatsApp]: WHATSAPP_TOKEN ayarlanmamis."

    phone_id = os.environ.get("WHATSAPP_PHONE_ID", "")
    if not phone_id:
        return "[WhatsApp]: WHATSAPP_PHONE_ID ayarlanmamis."

    try:
        r = requests.post(
            f"https://graph.facebook.com/v18.0/{phone_id}/messages",
            json={
                "messaging_product": "whatsapp",
                "to": hedef,
                "type": "text",
                "text": {"body": mesaj[:4096]},
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        if r.status_code == 200:
            return "[WhatsApp]: Mesaj gonderildi."
        return f"[WhatsApp]: Hata {r.status_code}"
    except Exception as e:
        return f"[WhatsApp]: Hata: {e}"



