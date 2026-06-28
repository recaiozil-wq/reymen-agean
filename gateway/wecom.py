# -*- coding: utf-8 -*-
"""gateway/wecom.py — WeCom (WeChat for Business) Platformu.

WeCom bot webhook'u uzerinden mesaj gonderir.
"""

import os
import requests


def baslat():
    pass


def durdur():
    pass


def mesaj_gonder(key: str, mesaj: str) -> str:
    """WeCom'a mesaj gonder.

    Args:
        key: Webhook key (bot'un webhook URL'sindeki key parametresi)
        mesaj: Mesaj icerigi

    Returns:
        Durum mesaji
    """
    if not key:
        key = os.environ.get("WECOM_WEBHOOK_KEY", "")
    if not key:
        return "[WeCom]: Webhook key gerekli."

    try:
        r = requests.post(
            f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={key}",
            json={"msgtype": "text", "text": {"content": mesaj[:2000]}},
            timeout=10,
        )
        data = r.json()
        if data.get("errcode") == 0:
            return "[WeCom]: Mesaj gonderildi."
        return f"[WeCom]: Hata {data.get('errmsg', 'bilinmiyor')}"
    except Exception as e:
        return f"[WeCom]: Hata: {e}"
