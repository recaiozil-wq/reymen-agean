# -*- coding: utf-8 -*-
"""gateway/platforms/bluebubbles.py — iMessage Platformu (BlueBubbles).

BlueBubbles server API'si uzerinden macOS iMessage gonderimi.
Windows'ta calismaz, sadece macOS + BlueBubbles server gerektirir.
"""

import os
import requests


def baslat():
    pass


def durdur():
    pass


def mesaj_gonder(hedef: str, mesaj: str) -> str:
    url = os.environ.get("BLUEBUBBLES_URL", "")
    token = os.environ.get("BLUEBUBBLES_TOKEN", "")
    if not url or not token:
        return "[BlueBubbles]: BLUEBUBBLES_URL/TOKEN ayarlanmamis."
    try:
        r = requests.post(
            f"{url}/api/v1/chat/message",
            json={"chatGuid": hedef, "text": mesaj[:4000]},
            headers={"Authorization": token},
            timeout=15,
        )
        return "[BlueBubbles]: Mesaj gonderildi." if r.status_code == 200 else f"[BlueBubbles]: Hata {r.status_code}"
    except Exception as e:
        return f"[BlueBubbles]: Hata: {e}"
