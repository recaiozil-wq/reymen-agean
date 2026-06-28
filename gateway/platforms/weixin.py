# -*- coding: utf-8 -*-
"""gateway/platforms/weixin.py — WeChat/WeiXin Platformu.

WeChat Official Account API'si uzerinden mesaj gonderir.
"""

import os
import requests


def baslat():
    pass


def durdur():
    pass


def mesaj_gonder(hedef: str, mesaj: str) -> str:
    """WeChat kullanicisina mesaj gonder.

    Args:
        hedef: Kullanici OpenID'si
        mesaj: Mesaj icerigi
    """
    appid = os.environ.get("WECHAT_APPID", "")
    secret = os.environ.get("WECHAT_SECRET", "")
    if not appid or not secret:
        return "[WeChat]: WECHAT_APPID/SECRET ayarlanmamis."

    try:
        # Access token al
        r = requests.get(
            f"https://api.weixin.qq.com/cgi-bin/token",
            params={"grant_type": "client_credential", "appid": appid, "secret": secret},
            timeout=10,
        )
        data = r.json()
        token = data.get("access_token")
        if not token:
            return f"[WeChat]: Token hatasi: {data}"

        # Mesaj gonder
        r2 = requests.post(
            f"https://api.weixin.qq.com/cgi-bin/message/custom/send",
            params={"access_token": token},
            json={"touser": hedef, "msgtype": "text", "text": {"content": mesaj[:2000]}},
            timeout=10,
        )
        return "[WeChat]: Mesaj gonderildi." if r2.status_code == 200 else f"[WeChat]: Hata {r2.status_code}"
    except Exception as e:
        return f"[WeChat]: Hata: {e}"
