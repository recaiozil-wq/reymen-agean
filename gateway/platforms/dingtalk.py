# -*- coding: utf-8 -*-
"""gateway/platforms/dingtalk.py — DingTalk Platformu.

DingTalk robot webhook'u uzerinden mesaj gonderir.
"""

import requests
from typing import Any


def baslat():
    pass


def durdur():
    pass


def mesaj_gonder(hedef: str, mesaj: str) -> str:
    """DingTalk webhook'una mesaj gonder.

    Args:
        hedef: Webhook URL'si
        mesaj: Mesaj icerigi
    """
    if not hedef.startswith("http"):
        return "[DingTalk]: Webhook URL'si gerekli."
    try:
        r = requests.post(
            hedef,
            json={"msgtype": "text", "text": {"content": mesaj[:2000]}},
            timeout=10,
        )
        return "[DingTalk]: Mesaj gonderildi." if r.status_code == 200 else f"[DingTalk]: Hata {r.status_code}"
    except Exception as e:
        return f"[DingTalk]: Hata: {e}"


class DingTalkAdapter:
    """DingTalk Adaptoru — upstream Hermes uyumluluk katmani.

    Gateway platform adapteri.
    """

    def __init__(self, config: Any = None):
        self._config = config

    def send_message(self, hedef: str, mesaj: str, **kwargs) -> str:
        return mesaj_gonder(hedef, mesaj)

    def ping(self) -> bool:
        return True
