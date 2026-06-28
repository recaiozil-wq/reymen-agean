# -*- coding: utf-8 -*-
"""gateway/platforms/matrix.py — Matrix Platformu.

Matrix homeserver uzerinden mesaj gonderir.
"""

import os
import requests
from typing import Any


def baslat():
    pass


def durdur():
    pass


def mesaj_gonder(hedef: str, mesaj: str) -> str:
    """Matrix odasina mesaj gonder.

    Args:
        hedef: Oda ID'si (!ode...rver.org)
        mesaj: Gonderilecek metin
    """
    token = os.environ.get("MATRIX_ACCESS_TOKEN", "")
    homeserver = os.environ.get("MATRIX_HOMESERVER", "https://matrix.org")

    if not token or token.startswith("***"):
        return "[Matrix]: MATRIX_ACCESS_TOKEN ayarlanmamis."

    try:
        # Once oda bilgisini al
        r = requests.post(
            f"{homeserver}/_matrix/client/v3/rooms/{hedef}/send/m.room.message",
            json={
                "msgtype": "m.text",
                "body": mesaj[:4000],
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        if r.status_code == 200:
            return "[Matrix]: Mesaj gonderildi."
        return f"[Matrix]: Hata {r.status_code}"
    except Exception as e:
        return f"[Matrix]: Hata: {e}"


class MatrixAdapter:
    """Matrix Adaptoru — upstream Hermes uyumluluk katmani.

    Gateway platform adapteri.
    """

    def __init__(self, config: Any = None):
        self._config = config

    def send_message(self, hedef: str, mesaj: str, **kwargs) -> str:
        return mesaj_gonder(hedef, mesaj)

    def ping(self) -> bool:
        return bool(os.environ.get("MATRIX_ACCESS_TOKEN", ""))



