# -*- coding: utf-8 -*-
"""gateway/platforms/wecom.py — WeCom (WeChat Work) Entegrasyonu.

Webhook ve API uzerinden mesaj gonderme.
"""

import os
import json
import logging
from typing import Any

try:
    import requests
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

logger = logging.getLogger(__name__)

_BASE_URL = "https://qyapi.weixin.qq.com/cgi-bin"


def _get_access_token() -> str:
    """WeCom access token al (corpid + corpsecret ile)."""
    corpid = os.environ.get("WECOM_CORP_ID", "")
    corpsecret = os.environ.get("WECOM_CORP_SECRET", "")
    if not corpid or not corpsecret:
        return ""
    try:
        r = requests.get(
            f"{_BASE_URL}/gettoken",
            params={"corpid": corpid, "corpsecret": corpsecret},
            timeout=10,
        )
        data = r.json()
        if data.get("errcode") == 0:
            return data.get("access_token", "")
        logger.warning("WeCom token hatasi: %s", data)
        return ""
    except Exception as e:
        logger.warning("WeCom token alinamadi: %s", e)
        return ""


def mesaj_gonder(hedef: str, mesaj: str, **kwargs) -> dict:
    """WeCom API uzerinden mesaj gonderir.

    Args:
        hedef: Alici (user ID, party ID, tag ID veya webhook URL)
        mesaj: Mesaj icerigi

    Keyword Args:
        msgtype: Mesaj tipi (text, markdown, image, news, etc.)
        agentid: WeCom agent ID (env'den WECOM_AGENT_ID okunur)
        webhook: True ise webhook uzerinden gonder

    Returns:
        dict: {"durum": "basarili", ...} veya hata
    """
    if not _REQUESTS_OK:
        return {"durum": "hata", "hata": "requests kutuphanesi yok."}

    webhook_mode = kwargs.get("webhook", False)
    if webhook_mode or hedef.startswith("http"):
        # Webhook uzerinden gonder
        url = hedef
        try:
            r = requests.post(
                url,
                json={"msgtype": "text", "text": {"content": mesaj[:2000]}},
                timeout=10,
            )
            data = r.json()
            if data.get("errcode") == 0:
                return {"durum": "basarili", "yontem": "webhook"}
            return {"durum": "hata", "hata": f"Webhook hatasi: {data}"}
        except Exception as e:
            return {"durum": "hata", "hata": str(e)}

    # API uzerinden gonder
    token = _get_access_token()
    if not token:
        return {"durum": "hata", "hata": "WeCom token alinamadi."}

    agent_id = kwargs.get("agentid") or os.environ.get("WECOM_AGENT_ID", "")
    if not agent_id:
        return {"durum": "hata", "hata": "WECOM_AGENT_ID ayarlanmamis."}

    msgtype = kwargs.get("msgtype", "text")

    content = {}
    if msgtype == "text":
        content = {"content": mesaj[:2000]}
    elif msgtype == "markdown":
        content = {"content": mesaj[:4096]}
    elif msgtype == "textcard":
        content = {
            "title": kwargs.get("title", mesaj[:50]),
            "description": mesaj[:500],
            "url": kwargs.get("url", ""),
            "btntxt": kwargs.get("buton", "Detay"),
        }
    else:
        content = {"content": mesaj[:2000]}

    try:
        r = requests.post(
            f"{_BASE_URL}/message/send?access_token={token}",
            json={
                "touser": hedef,
                "msgtype": msgtype,
                "agentid": int(agent_id),
                msgtype: content,
            },
            timeout=10,
        )
        data = r.json()
        if data.get("errcode") == 0:
            return {"durum": "basarili", "msgid": data.get("msgid", "")}
        return {"durum": "hata", "hata": f"API hatasi {data.get('errcode')}: {data.get('errmsg', '')}"}
    except Exception as e:
        return {"durum": "hata", "hata": str(e)}


def send_message(hedef: str, mesaj: str, **kwargs) -> dict:
    """Dis arayuz — mesaj_gonder alias."""
    return mesaj_gonder(hedef, mesaj, **kwargs)


def ping() -> bool:
    """WeCom baglantisini kontrol eder."""
    token = _get_access_token()
    return bool(token)


class WeComAdapter:
    """WeCom (WeChat Work) Adaptoru — upstream Hermes uyumluluk katmani.

    Gateway platform adapteri.
    """

    def __init__(self, config: Any = None):
        self._config = config

    def send_message(self, hedef: str, mesaj: str, **kwargs) -> dict:
        return mesaj_gonder(hedef, mesaj, **kwargs)

    def ping(self) -> bool:
        return ping()
