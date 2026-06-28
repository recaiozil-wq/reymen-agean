# -*- coding: utf-8 -*-
"""gateway/sms.py — SMS Platform Gateway.

Twilio veya yerel SMS gateway üzerinden SMS gönderim/alım.
ENV: SMS_PROVIDER=twilio|local, TWILIO_SID, TWILIO_TOKEN, TWILIO_FROM
"""

import json
import os
import urllib.parse
import urllib.request
from typing import Callable, Optional

SMS_PROVIDER   = os.environ.get("SMS_PROVIDER",   "twilio")
TWILIO_SID     = os.environ.get("TWILIO_SID",     "")
TWILIO_TOKEN   = os.environ.get("TWILIO_TOKEN",   "")
TWILIO_FROM    = os.environ.get("TWILIO_FROM",    "")
SMS_IZIN_LISTE = [n.strip() for n in
                  os.environ.get("SMS_ALLOWED_NUMBERS", "").split(",") if n.strip()]


def _twilio_gonder(alici: str, mesaj: str) -> str:
    if not all([TWILIO_SID, TWILIO_TOKEN, TWILIO_FROM]):
        return "[SMS]: Twilio kimlik bilgileri eksik."
    url  = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json"
    veri = urllib.parse.urlencode({
        "To":   alici,
        "From": TWILIO_FROM,
        "Body": mesaj[:1600],
    }).encode("utf-8")
    import base64
    token = base64.b64encode(f"{TWILIO_SID}:{TWILIO_TOKEN}".encode()).decode()
    try:
        req = urllib.request.Request(
            url, data=veri,
            headers={"Authorization": f"Basic {token}"},
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            yanit = json.loads(r.read().decode("utf-8"))
            return f"[SMS]: Gönderildi (SID: {yanit.get('sid','?')})"
    except Exception as e:
        return f"[SMS]: Hata — {e}"


def sms_gonder(alici: str, mesaj: str) -> str:
    """SMS gönder.

    Args:
        alici: Telefon numarası (+90...)
        mesaj: Metin (max 1600 karakter)
    """
    if SMS_IZIN_LISTE and alici not in SMS_IZIN_LISTE:
        return f"[SMS]: {alici} izin listesinde değil."
    if SMS_PROVIDER == "twilio":
        return _twilio_gonder(alici, mesaj)
    return f"[SMS]: Bilinmeyen sağlayıcı: {SMS_PROVIDER}"


class SMSGateway:
    """SMS gateway — gönderim + basit polling."""

    def __init__(self):
        self._isleyici: Optional[Callable] = None
        self._gecmis: list[dict] = []

    def mesaj_isleyici_kaydet(self, fn: Callable):
        self._isleyici = fn

    def gonder(self, alici: str, mesaj: str) -> str:
        sonuc = sms_gonder(alici, mesaj)
        self._gecmis.append({"yon": "cikis", "alici": alici, "mesaj": mesaj[:80]})
        return sonuc

    def mesaj_al(self, gonderen: str, mesaj: str):
        """Gelen SMS — webhook veya polling ile tetiklenir."""
        self._gecmis.append({"yon": "giris", "gonderen": gonderen, "mesaj": mesaj[:80]})
        if self._isleyici:
            self._isleyici(mesaj, "sms", {"gonderen": gonderen})

    def gecmis(self, n: int = 10) -> list[dict]:
        return self._gecmis[-n:]

    def yapilandirildi_mi(self) -> bool:
        return SMS_PROVIDER == "twilio" and bool(TWILIO_SID and TWILIO_TOKEN)


def motor_kaydet(motor):
    """SMS_GONDER aracını motora kaydet."""
    def _sms_gonder(alici: str, mesaj: str) -> str:
        return sms_gonder(alici, mesaj)

    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet("SMS_GONDER", _sms_gonder, "SMS gönder")


if __name__ == "__main__":
    gw = SMSGateway()
    print(f"Yapılandırıldı: {gw.yapilandirildi_mi()}")
    gw.mesaj_al("+905551234567", "merhaba")
    print(gw.gecmis())
