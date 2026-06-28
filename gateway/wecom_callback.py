# -*- coding: utf-8 -*-
"""gateway/wecom_callback.py — WeCom Callback Isleyici.

WeCom mesaj callback URL'sini dogrular ve isler.
"""

import hashlib
import xml.etree.ElementTree as ET


def dogrula(msg_signature: str, timestamp: str, nonce: str, echo_str: str, token: str) -> bool:
    """WeCom callback dogrulaması.

    Args:
        msg_signature: Mesaj imzasi
        timestamp: Zaman damgasi
        nonce: Rastgele sayi
        echo_str: Echo string (URL dogrulama icin)
        token: Bot token'i

    Returns:
        Dogrulama basarili mi?
    """
    if not token:
        return False
    s = "".join(sorted([token, timestamp, nonce, echo_str or ""]))
    imza = hashlib.sha1(s.encode("utf-8")).hexdigest()
    return imza == msg_signature


def mesaj_coz(xml_veri: str) -> dict:
    """XML mesaji coz.

    Args:
        xml_veri: WeChat XML formati

    Returns:
        {"from": str, "content": str, "msgtype": str}
    """
    try:
        root = ET.fromstring(xml_veri)
        return {
            "from": root.findtext("FromUserName", ""),
            "content": root.findtext("Content", ""),
            "msgtype": root.findtext("MsgType", ""),
            "msgid": root.findtext("MsgId", ""),
        }
    except Exception:
        return {"from": "", "content": "", "msgtype": ""}


if __name__ == "__main__":
    print(dogrula("test", "123", "abc", "echo", "token"))
