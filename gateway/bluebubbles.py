# -*- coding: utf-8 -*-
"""gateway/bluebubbles.py — BlueBubbles iMessage Gateway.

BlueBubbles sunucusu üzerinden iMessage gönderim/alım.
ENV: BLUEBUBBLES_URL, BLUEBUBBLES_PASSWORD
"""

import json
import os
import urllib.parse
import urllib.request
from typing import Callable, Optional

BB_URL      = os.environ.get("BLUEBUBBLES_URL",      "http://localhost:1234")
BB_PASSWORD = os.environ.get("BLUEBUBBLES_PASSWORD", "")


def _istek(yontem: str, yol: str, veri: Optional[dict] = None) -> dict:
    params = urllib.parse.urlencode({"password": BB_PASSWORD})
    url    = f"{BB_URL.rstrip('/')}{yol}?{params}"
    govde  = json.dumps(veri or {}).encode("utf-8") if veri else None
    try:
        req = urllib.request.Request(
            url, data=govde,
            headers={"Content-Type": "application/json"},
            method=yontem,
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e), "status": 500}


class BlueBubblesGateway:
    """BlueBubbles iMessage gateway."""

    def __init__(self):
        self._isleyici: Optional[Callable] = None

    def gonder(self, alici: str, mesaj: str, ek_dosya: str = "") -> str:
        """iMessage gönder.

        Args:
            alici:    Telefon numarası veya Apple ID
            mesaj:    Metin içeriği
            ek_dosya: Dosya yolu (opsiyonel)
        """
        if not BB_PASSWORD:
            return "[iMessage]: BLUEBUBBLES_PASSWORD ayarlanmamış."
        yanit = _istek("POST", "/api/v1/message/text", {
            "chatGuid": f"iMessage;-;{alici}",
            "message":  mesaj,
            "method":   "apple-script",
        })
        if yanit.get("status") == 200:
            return f"[iMessage]: Gönderildi → {alici}"
        return f"[iMessage]: Hata — {yanit.get('error', yanit)}"

    def sohbetleri_listele(self, limit: int = 20) -> list[dict]:
        yanit = _istek("GET", f"/api/v1/chat?limit={limit}&offset=0")
        return yanit.get("data", [])

    def mesajlari_oku(self, sohbet_guid: str, limit: int = 10) -> list[dict]:
        yanit = _istek("GET", f"/api/v1/chat/{urllib.parse.quote(sohbet_guid)}/message?limit={limit}")
        return yanit.get("data", [])

    def mesaj_isleyici_kaydet(self, fn: Callable):
        self._isleyici = fn

    def webhook_isle(self, veri: dict):
        """BlueBubbles webhook eventi işle."""
        tip   = veri.get("type", "")
        if tip == "new-message":
            mesaj   = veri.get("data", {})
            metin   = mesaj.get("text", "")
            gonderen= mesaj.get("handle", {}).get("address", "?")
            if metin and not mesaj.get("isFromMe") and self._isleyici:
                self._isleyici(metin, "imessage", {"gonderen": gonderen})

    def saglik_kontrol(self) -> bool:
        yanit = _istek("GET", "/api/v1/ping")
        return yanit.get("message") == "pong"

    def yapilandirildi_mi(self) -> bool:
        return bool(BB_URL and BB_PASSWORD)


def motor_kaydet(motor):
    gw = BlueBubblesGateway()
    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet(
            "IMESSAGE_GONDER",
            lambda alici, mesaj: gw.gonder(alici, mesaj),
            "iMessage gönder (BlueBubbles)",
        )


if __name__ == "__main__":
    gw = BlueBubblesGateway()
    print(f"Yapılandırıldı: {gw.yapilandirildi_mi()}")
    if gw.yapilandirildi_mi():
        print(f"Sağlık: {gw.saglik_kontrol()}")
