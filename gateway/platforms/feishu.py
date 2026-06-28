# -*- coding: utf-8 -*-
"""gateway/platforms/feishu.py — Feishu/Lark Platformu.

Feishu bot API'si uzerinden mesaj gonderir.
"""

import os
import requests
from typing import Any


def baslat():
    pass


def durdur():
    pass


def mesaj_gonder(hedef: str, mesaj: str) -> str:
    token = os.environ.get("FEISHU_TOKEN", "")
    if not token:
        return "[Feishu]: FEISHU_TOKEN ayarlanmamis."
    try:
        r = requests.post(
            f"https://open.feishu.cn/open-apis/im/v1/messages",
            json={"receive_id": hedef, "msg_type": "text", "content": f'{{"text":"{mesaj[:2000]}"}}'},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        return "[Feishu]: Mesaj gonderildi." if r.status_code == 200 else f"[Feishu]: Hata {r.status_code}"
    except Exception as e:
        return f"[Feishu]: Hata: {e}"


class FeishuAdapter:
    """Feishu/Lark Adaptoru — upstream Hermes uyumluluk katmani.

    Gateway platform adapteri olarak send_message, ping metodlarini uygular.
    """

    def __init__(self, config: Any = None):
        self._config = config

    def send_message(self, hedef: str, mesaj: str, **kwargs) -> str:
        return mesaj_gonder(hedef, mesaj)

    def ping(self) -> bool:
        return bool(os.environ.get("FEISHU_TOKEN", ""))
