# -*- coding: utf-8 -*-
"""gateway/platforms/sms.py — SMS Platformu.

Twilio API ile SMS gonderimi.
"""

import os
import logging

logger = logging.getLogger("gateway.sms")


def baslat():
    pass


def durdur():
    pass


def mesaj_gonder(hedef: str, mesaj: str) -> str:
    """SMS gonder.

    Args:
        hedef: Telefon numarasi (+90xxxxxxxxx)
        mesaj: SMS metni (max 1600 karakter)

    Returns:
        Durum mesaji
    """
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
    from_num = os.environ.get("TWILIO_FROM_NUMBER", "")

    if not account_sid or not auth_token:
        return "[SMS]: Twilio credentials ayarlanmamis."

    try:
        from twilio.rest import Client
        client = Client(account_sid, auth_token)
        msg = client.messages.create(
            body=mesaj[:1600],
            from_=from_num,
            to=hedef,
        )
        return f"[SMS]: Gonderildi (SID: {msg.sid[:20]}...)"
    except ImportError:
        return "[SMS]: twilio kutuphanesi yok (pip install twilio)"
    except Exception as e:
        return f"[SMS]: Hata: {e}"
