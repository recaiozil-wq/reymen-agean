# -*- coding: utf-8 -*-
"""gateway/platforms/webhook.py — Webhook Platformu.

HTTP POST ile herhangi bir webhook URL'sine mesaj gonderir.
"""

import os
import json
import requests


def baslat():
    pass


def durdur():
    pass


class WebhookAdapter:
    """Webhook platform adaptörü — gateway/run.py ve testler için."""

    platform = "webhook"

    def __init__(self):
        self._mesaj_isleyici = None

    def mesaj_isleyici_kaydet(self, fn):
        """Gelen mesaj işleyici fonksiyonunu kaydet."""
        self._mesaj_isleyici = fn

    async def send_message(self, hedef: str, mesaj: str, **kwargs) -> dict:
        """Async mesaj gönder."""
        try:
            sonuc = mesaj_gonder(hedef, mesaj)
            if "Gonderildi" in sonuc or "Gönderildi" in sonuc:
                return {"durum": "basarili", "sonuc": sonuc}
            return {"durum": "hata", "hata": sonuc}
        except Exception as e:
            return {"durum": "hata", "hata": str(e)}

    def ping(self) -> bool:
        return True


def mesaj_gonder(hedef: str, mesaj: str) -> str:
    """Webhook URL'sine POST istegi gonder.

    Args:
        hedef: Webhook URL'si
        mesaj: Gonderilecek veri

    Returns:
        Durum mesaji
    """
    if not hedef.startswith("http"):
        return "[Webhook]: Gecerli bir URL gerekli."

    try:
        payload = {
            "text": mesaj[:4000],
            "source": "ReYMeN",
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }
        r = requests.post(
            hedef,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        if 200 <= r.status_code < 300:
            return f"[Webhook]: Gonderildi (HTTP {r.status_code})."
        return f"[Webhook]: Hata {r.status_code}: {r.text[:100]}"
    except requests.Timeout:
        return "[Webhook]: Zaman asimi."
    except Exception as e:
        return f"[Webhook]: Hata: {e}"
