# -*- coding: utf-8 -*-
"""gateway/feishu.py — Feishu/Lark Platform Gateway.

Feishu (Lark) bot webhook ve API entegrasyonu.
ENV: FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_VERIFICATION_TOKEN
"""

import hashlib
import json
import os
import time
import urllib.request
from typing import Callable, Optional

FEISHU_APP_ID    = os.environ.get("FEISHU_APP_ID",    "")
FEISHU_APP_SECRET= os.environ.get("FEISHU_APP_SECRET","")
FEISHU_TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
FEISHU_MSG_URL   = "https://open.feishu.cn/open-apis/im/v1/messages"


def _istek(yontem: str, url: str, veri: Optional[dict] = None, token: str = "") -> dict:
    govde = json.dumps(veri or {}).encode("utf-8") if veri else None
    basliklar = {"Content-Type": "application/json"}
    if token:
        basliklar["Authorization"] = f"Bearer {token}"
    try:
        req = urllib.request.Request(url, data=govde, headers=basliklar, method=yontem)
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


class FeishuGateway:
    """Feishu/Lark mesajlaşma gateway."""

    def __init__(self):
        self._token: str = ""
        self._token_bitis: float = 0.0
        self._isleyici: Optional[Callable] = None

    def _erisim_token(self) -> str:
        if time.time() < self._token_bitis and self._token:
            return self._token
        if not (FEISHU_APP_ID and FEISHU_APP_SECRET):
            return ""
        yanit = _istek("POST", FEISHU_TOKEN_URL, {
            "app_id":     FEISHU_APP_ID,
            "app_secret": FEISHU_APP_SECRET,
        })
        self._token      = yanit.get("tenant_access_token", "")
        self._token_bitis= time.time() + yanit.get("expire", 7200) - 60
        return self._token

    def gonder(self, alici_id: str, mesaj: str, mesaj_tipi: str = "text") -> str:
        """Feishu'ya mesaj gönder.

        Args:
            alici_id:   open_id veya chat_id
            mesaj:      Metin içeriği
            mesaj_tipi: "text" | "post" | "interactive"
        """
        token = self._erisim_token()
        if not token:
            return "[Feishu]: Token alınamadı — APP_ID/SECRET kontrol et."

        if mesaj_tipi == "text":
            icerik = json.dumps({"text": mesaj})
        else:
            icerik = mesaj

        yanit = _istek("POST", FEISHU_MSG_URL, {
            "receive_id": alici_id,
            "msg_type":   mesaj_tipi,
            "content":    icerik,
        }, token=token)

        if yanit.get("code") == 0:
            return f"[Feishu]: Gönderildi (msg_id: {yanit.get('data',{}).get('message_id','?')})"
        return f"[Feishu]: Hata {yanit.get('code')} — {yanit.get('msg','?')}"

    def mesaj_isleyici_kaydet(self, fn: Callable):
        self._isleyici = fn

    def webhook_isle(self, veri: dict) -> dict:
        """Feishu webhook eventi işle."""
        header  = veri.get("header", {})
        tip     = header.get("event_type", "")
        event   = veri.get("event", {})

        if tip == "im.message.receive_v1":
            mesaj   = event.get("message", {})
            gonderen= event.get("sender", {}).get("sender_id", {}).get("open_id", "?")
            icerik  = mesaj.get("content", "{}")
            try:
                metin = json.loads(icerik).get("text", icerik)
            except Exception:
                metin = icerik

            if self._isleyici:
                self._isleyici(metin, "feishu", {"gonderen": gonderen})

        return {"code": 0}

    def yapilandirildi_mi(self) -> bool:
        return bool(FEISHU_APP_ID and FEISHU_APP_SECRET)


def motor_kaydet(motor):
    gw = FeishuGateway()
    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet(
            "FEISHU_GONDER",
            lambda alici, mesaj: gw.gonder(alici, mesaj),
            "Feishu/Lark mesajı gönder",
        )


if __name__ == "__main__":
    gw = FeishuGateway()
    print(f"Yapılandırıldı: {gw.yapilandirildi_mi()}")
