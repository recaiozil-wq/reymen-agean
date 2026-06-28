# -*- coding: utf-8 -*-
"""gateway/platforms/homeassistant.py — Home Assistant Platformu.

Home Assistant REST API uzerinden durum sorgulama ve kontrol.
"""

import os
import requests


def baslat():
    pass


def durdur():
    pass


def mesaj_gonder(hedef: str, mesaj: str) -> str:
    """Home Assistant'a bildirim gonder.

    Args:
        hedef: Entity ID veya notify servis adi
        mesaj: Bildirim mesaji
    """
    url = os.environ.get("HA_URL", "http://homeassistant.local:8123")
    token = os.environ.get("HA_TOKEN", "")
    if not token:
        return "[HA]: HA_TOKEN ayarlanmamis."
    try:
        r = requests.post(
            f"{url}/api/services/notify/{hedef}",
            json={"message": mesaj[:2000]},
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            timeout=10,
        )
        return "[HA]: Bildirim gonderildi." if r.status_code == 200 else f"[HA]: Hata {r.status_code}"
    except Exception as e:
        return f"[HA]: Hata: {e}"
