# -*- coding: utf-8 -*-
"""gateway/qqbot/__init__.py — QQ Bot Platformu.

QQ bot API'si uzerinden mesaj gonderimi (QQ kanal bot).
"""


__all__ = ['baslat', 'durdur', 'mesaj_gonder']
import os
import requests


def baslat():
    pass


def durdur():
    pass


def mesaj_gonder(hedef: str, mesaj: str) -> str:
    """QQ kanalina mesaj gonder.

    Args:
        hedef: Kanal ID'si veya kullanici ID'si
        mesaj: Mesaj icerigi

    Returns:
        Durum mesaji
    """
    token = os.environ.get("QQ_BOT_TOKEN", "")
    appid = os.environ.get("QQ_BOT_APPID", "")
    if not token or not appid:
        return "[QQBot]: QQ_BOT_TOKEN/APPID ayarlanmamis."

    try:
        r = requests.post(
            f"https://api.sgroup.qq.com/channels/{hedef}/messages",
            json={"content": mesaj[:2000]},
            headers={"Authorization": f"Bot {appid}.{token}"},
            timeout=10,
        )
        if r.status_code == 200:
            return "[QQBot]: Mesaj gonderildi."
        return f"[QQBot]: Hata {r.status_code}"
    except Exception as e:
        return f"[QQBot]: Hata: {e}"
