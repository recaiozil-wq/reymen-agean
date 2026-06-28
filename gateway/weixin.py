# -*- coding: utf-8 -*-
"""gateway/weixin.py — WeChat (Weixin) Platform Gateway.

WeChat Official Account API entegrasyonu.
ENV: WECHAT_APP_ID, WECHAT_APP_SECRET, WECHAT_TOKEN (webhook doğrulama)
"""

import hashlib
import json
import os
import time
import urllib.request
from typing import Callable, Optional

WECHAT_APP_ID     = os.environ.get("WECHAT_APP_ID",     "")
WECHAT_APP_SECRET = os.environ.get("WECHAT_APP_SECRET", "")
WECHAT_TOKEN      = os.environ.get("WECHAT_TOKEN",      "")

_ACCESS_TOKEN_CACHE: dict = {"token": "", "bitis": 0.0}


def _erisim_token() -> str:
    if time.time() < _ACCESS_TOKEN_CACHE["bitis"] and _ACCESS_TOKEN_CACHE["token"]:
        return _ACCESS_TOKEN_CACHE["token"]
    if not (WECHAT_APP_ID and WECHAT_APP_SECRET):
        return ""
    url = (f"https://api.weixin.qq.com/cgi-bin/token"
           f"?grant_type=client_credential"
           f"&appid={WECHAT_APP_ID}&secret={WECHAT_APP_SECRET}")
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            yanit = json.loads(r.read().decode("utf-8"))
            _ACCESS_TOKEN_CACHE["token"] = yanit.get("access_token", "")
            _ACCESS_TOKEN_CACHE["bitis"] = time.time() + yanit.get("expires_in", 7200) - 60
            return _ACCESS_TOKEN_CACHE["token"]
    except Exception:
        return ""


class WeixinGateway:
    """WeChat Official Account gateway."""

    def __init__(self):
        self._isleyici: Optional[Callable] = None

    def _istek(self, yol: str, veri: dict) -> dict:
        token = _erisim_token()
        if not token:
            return {"errcode": -1, "errmsg": "token yok"}
        url   = f"https://api.weixin.qq.com{yol}?access_token={token}"
        govde = json.dumps(veri, ensure_ascii=False).encode("utf-8")
        try:
            req = urllib.request.Request(
                url, data=govde,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            return {"errcode": -1, "errmsg": str(e)}

    def metin_gonder(self, openid: str, metin: str) -> str:
        yanit = self._istek("/cgi-bin/message/custom/send", {
            "touser":  openid,
            "msgtype": "text",
            "text":    {"content": metin[:600]},
        })
        if yanit.get("errcode") == 0:
            return "[WeChat]: Gönderildi."
        return f"[WeChat]: Hata {yanit.get('errcode')} — {yanit.get('errmsg','?')}"

    def webhook_dogrula(self, signature: str, timestamp: str, nonce: str) -> bool:
        """WeChat webhook imzasını doğrula."""
        if not WECHAT_TOKEN:
            return True
        degerler = sorted([WECHAT_TOKEN, timestamp, nonce])
        hesaplanan = hashlib.sha1("".join(degerler).encode()).hexdigest()
        return hesaplanan == signature

    def webhook_isle(self, xml_icerik: str) -> str:
        """Gelen XML mesajı parse et ve işle."""
        import re
        def _cek(etiket: str) -> str:
            m = re.search(fr"<{etiket}><!\[CDATA\[(.*?)\]\]></{etiket}>", xml_icerik)
            if not m:
                m = re.search(fr"<{etiket}>(.*?)</{etiket}>", xml_icerik)
            return m.group(1).strip() if m else ""

        msg_type = _cek("MsgType")
        from_user= _cek("FromUserName")
        metin    = _cek("Content") if msg_type == "text" else f"[{msg_type}]"

        if metin and self._isleyici:
            self._isleyici(metin, "weixin", {"openid": from_user})
        return "success"

    def mesaj_isleyici_kaydet(self, fn: Callable):
        self._isleyici = fn

    def yapilandirildi_mi(self) -> bool:
        return bool(WECHAT_APP_ID and WECHAT_APP_SECRET)


def motor_kaydet(motor):
    gw = WeixinGateway()
    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet(
            "WECHAT_GONDER",
            lambda openid, mesaj: gw.metin_gonder(openid, mesaj),
            "WeChat kullanıcısına mesaj gönder",
        )


if __name__ == "__main__":
    gw = WeixinGateway()
    print(f"Yapılandırıldı: {gw.yapilandirildi_mi()}")
