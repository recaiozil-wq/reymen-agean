# -*- coding: utf-8 -*-
"""gateway/dingtalk.py — DingTalk Platform Gateway.

DingTalk robot webhook entegrasyonu.
ENV: DINGTALK_WEBHOOK, DINGTALK_SECRET (HMAC imza doğrulama)
"""

import base64
import hashlib
import hmac
import json
import os
import time
import urllib.parse
import urllib.request
from typing import Callable, Optional

DINGTALK_WEBHOOK = os.environ.get("DINGTALK_WEBHOOK", "")
DINGTALK_SECRET  = os.environ.get("DINGTALK_SECRET",  "")


def _imzali_url() -> str:
    """Zaman damgalı HMAC-SHA256 imzalı URL üret."""
    ts = str(int(time.time() * 1000))
    metin = f"{ts}\n{DINGTALK_SECRET}"
    imza = base64.b64encode(
        hmac.new(DINGTALK_SECRET.encode("utf-8"),
                 metin.encode("utf-8"),
                 digestmod=hashlib.sha256).digest()
    ).decode("utf-8")
    imza_enc = urllib.parse.quote_plus(imza)
    return f"{DINGTALK_WEBHOOK}&timestamp={ts}&sign={imza_enc}"


def _gonder(veri: dict) -> str:
    if not DINGTALK_WEBHOOK:
        return "[DingTalk]: DINGTALK_WEBHOOK ayarlanmamış."
    url = _imzali_url() if DINGTALK_SECRET else DINGTALK_WEBHOOK
    govde = json.dumps(veri, ensure_ascii=False).encode("utf-8")
    try:
        req = urllib.request.Request(
            url, data=govde,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            yanit = json.loads(r.read().decode("utf-8"))
            if yanit.get("errcode") == 0:
                return "[DingTalk]: Gönderildi."
            return f"[DingTalk]: Hata {yanit.get('errcode')} — {yanit.get('errmsg','?')}"
    except Exception as e:
        return f"[DingTalk]: Hata — {e}"


class DingTalkGateway:
    """DingTalk mesajlaşma gateway."""

    def __init__(self):
        self._isleyici: Optional[Callable] = None

    def mesaj_gonder(self, metin: str) -> str:
        return _gonder({"msgtype": "text", "text": {"content": metin}})

    def markdown_gonder(self, baslik: str, metin: str) -> str:
        return _gonder({
            "msgtype": "markdown",
            "markdown": {"title": baslik, "text": metin},
        })

    def at_ile_gonder(self, metin: str, telefon_numaralari: list[str]) -> str:
        return _gonder({
            "msgtype": "text",
            "text":    {"content": metin},
            "at":      {"atMobiles": telefon_numaralari, "isAtAll": False},
        })

    def mesaj_isleyici_kaydet(self, fn: Callable):
        self._isleyici = fn

    def webhook_isle(self, veri: dict) -> dict:
        """DingTalk gelen webhook eventi işle."""
        metin    = (veri.get("text", {}).get("content", "")
                    or veri.get("content", {}).get("content", "")).strip()
        gonderen = veri.get("senderNick", "?")
        if metin and self._isleyici:
            self._isleyici(metin, "dingtalk", {"gonderen": gonderen})
        return {"msgtype": "empty"}

    def yapilandirildi_mi(self) -> bool:
        return bool(DINGTALK_WEBHOOK)


def motor_kaydet(motor):
    gw = DingTalkGateway()
    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet(
            "DINGTALK_GONDER",
            lambda mesaj: gw.mesaj_gonder(mesaj),
            "DingTalk robota mesaj gönder",
        )


if __name__ == "__main__":
    gw = DingTalkGateway()
    print(f"Yapılandırıldı: {gw.yapilandirildi_mi()}")
    if gw.yapilandirildi_mi():
        print(gw.mesaj_gonder("ReYMeN test mesajı"))
