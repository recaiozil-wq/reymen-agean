# -*- coding: utf-8 -*-
"""gateway/homeassistant.py — Home Assistant Gateway.

Home Assistant REST API üzerinden akıllı ev kontrolü.
ENV: HA_URL, HA_TOKEN
"""

import json
import os
import urllib.request
from typing import Any, Callable, Optional

HA_URL   = os.environ.get("HA_URL",   "http://homeassistant.local:8123")
HA_TOKEN = os.environ.get("HA_TOKEN", "")


def _istek(yontem: str, yol: str, veri: Optional[dict] = None) -> dict:
    if not HA_TOKEN:
        return {"error": "HA_TOKEN ayarlanmamış."}
    url    = f"{HA_URL.rstrip('/')}{yol}"
    govde  = json.dumps(veri or {}).encode("utf-8") if veri else None
    try:
        req = urllib.request.Request(
            url, data=govde,
            headers={
                "Authorization": f"Bearer {HA_TOKEN}",
                "Content-Type":  "application/json",
            },
            method=yontem,
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            try:
                return json.loads(r.read().decode("utf-8"))
            except Exception:
                return {"status": r.getcode()}
    except Exception as e:
        return {"error": str(e)}


class HomeAssistantGateway:
    """Home Assistant akıllı ev gateway."""

    def __init__(self):
        self._isleyici: Optional[Callable] = None

    def servis_cagir(self, alan: str, servis: str, entity_id: str, **kwargs) -> str:
        """HA servisi çağır (örn: light.turn_on, switch.toggle).

        Args:
            alan:      Servis alanı (light, switch, climate, ...)
            servis:    Servis adı (turn_on, turn_off, toggle)
            entity_id: Varlık kimliği
        """
        veri = {"entity_id": entity_id, **kwargs}
        yanit = _istek("POST", f"/api/services/{alan}/{servis}", veri)
        if "error" in yanit:
            return f"[HA]: Hata — {yanit['error']}"
        return f"[HA]: {alan}.{servis} → {entity_id} ✓"

    def durum_oku(self, entity_id: str) -> dict:
        """Bir varlığın mevcut durumunu oku."""
        return _istek("GET", f"/api/states/{entity_id}")

    def tum_durumlar(self) -> list[dict]:
        """Tüm HA varlık durumlarını listele."""
        yanit = _istek("GET", "/api/states")
        return yanit if isinstance(yanit, list) else []

    def olay_tetikle(self, olay_tipi: str, olay_verisi: Optional[dict] = None) -> str:
        yanit = _istek("POST", f"/api/events/{olay_tipi}", olay_verisi or {})
        if "error" in yanit:
            return f"[HA]: Olay hatası — {yanit['error']}"
        return f"[HA]: Olay tetiklendi: {olay_tipi}"

    def saglik_kontrol(self) -> bool:
        yanit = _istek("GET", "/api/")
        return "message" in yanit

    def mesaj_isleyici_kaydet(self, fn: Callable):
        self._isleyici = fn

    def webhook_isle(self, veri: dict):
        """HA webhook/notification eventi."""
        mesaj = veri.get("message", str(veri))
        if mesaj and self._isleyici:
            self._isleyici(mesaj, "homeassistant", veri)

    def yapilandirildi_mi(self) -> bool:
        return bool(HA_URL and HA_TOKEN)


def motor_kaydet(motor):
    gw = HomeAssistantGateway()
    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet(
            "HA_SERVIS",
            lambda alan, servis, entity_id: gw.servis_cagir(alan, servis, entity_id),
            "Home Assistant servisi çağır",
        )
        motor._plugin_arac_kaydet(
            "HA_DURUM",
            lambda entity_id: str(gw.durum_oku(entity_id)),
            "Home Assistant varlık durumu oku",
        )


if __name__ == "__main__":
    gw = HomeAssistantGateway()
    print(f"Yapılandırıldı: {gw.yapilandirildi_mi()}")
    if gw.yapilandirildi_mi():
        print(f"Sağlık: {gw.saglik_kontrol()}")
        print(gw.servis_cagir("light", "turn_on", "light.salon"))
