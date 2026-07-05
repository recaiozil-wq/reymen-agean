# -*- coding: utf-8 -*-
"""yuanbao_tools.py â€” Tencent Yuanbao (å…ƒå®) AraçlarÄ±.

Tencent Yuanbao AI asistanÄ± API entegrasyonu.
Hunyuan modelini destekler; Ã‡ince NLP görevleri için idealdir.
ENV: YUANBAO_APP_ID, YUANBAO_SECRET_KEY
"""

import hashlib
import hmac
import json
import os
import time
import urllib.parse
import urllib.request
from typing import Optional

YUANBAO_APP_ID = os.environ.get("YUANBAO_APP_ID", "")
YUANBAO_SECRET_KEY = os.environ.get("YUANBAO_SECRET_KEY", "")
YUANBAO_REGION = os.environ.get("YUANBAO_REGION", "ap-guangzhou")
HUNYUAN_BASE = "https://hunyuan.tencentcloudapi.com"


def _imza_uret(yuk: str, zaman_damgasi: int, nonce: str) -> str:
    """Tencent Cloud API v3 HMAC-SHA256 imzasÄ±."""
    if not YUANBAO_SECRET_KEY:
        return ""
    mesaj = f"{zaman_damgasi}\n{nonce}\n{yuk}"
    return hmac.new(
        YUANBAO_SECRET_KEY.encode("utf-8"),
        mesaj.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _hunyuan_istek(eylem: str, govde: dict) -> dict:
    """Hunyuan API'ye istek gönder."""
    if not YUANBAO_APP_ID or not YUANBAO_SECRET_KEY:
        return {"error": "YUANBAO_APP_ID veya YUANBAO_SECRET_KEY ayarlanmamÄ±ÅŸ."}

    zaman_damgasi = int(time.time())
    nonce = str(zaman_damgasi)
    yuk_json = json.dumps(govde, ensure_ascii=False)
    imza = _imza_uret(yuk_json, zaman_damgasi, nonce)

    basliklar = {
        "Content-Type": "application/json",
        "X-TC-Action": eylem,
        "X-TC-Version": "2023-09-01",
        "X-TC-Timestamp": str(zaman_damgasi),
        "X-TC-Region": YUANBAO_REGION,
        "X-TC-RequestClient": "ReYMeN/1.0",
        "Authorization": (
            f"TC3-HMAC-SHA256 Credential={YUANBAO_APP_ID},"
            f" SignedHeaders=content-type;host, Signature={imza}"
        ),
    }

    try:
        req = urllib.request.Request(
            HUNYUAN_BASE,
            data=yuk_json.encode("utf-8"),
            headers=basliklar,
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8")).get("Response", {})
    except Exception as e:
        return {"error": str(e)}


def hunyuan_sohbet(
    mesaj: str,
    sistem: str = "Sen yardÄ±mcÄ± bir AI asistanÄ±sÄ±n.",
    model: str = "hunyuan-lite",
) -> str:
    """Hunyuan modeline soru sor.

    Args:
        mesaj:  KullanÄ±cÄ± mesajÄ±
        sistem: Sistem promptu
        model:  hunyuan-lite | hunyuan-standard | hunyuan-pro

    Returns:
        YanÄ±t metni
    """
    yanit = _hunyuan_istek(
        "ChatCompletions",
        {
            "Model": model,
            "Messages": [
                {"Role": "system", "Content": sistem},
                {"Role": "user", "Content": mesaj},
            ],
        },
    )

    if "error" in yanit:
        return f"[Yuanbao]: {yanit['error']}"

    secimler = yanit.get("Choices", [])
    if secimler:
        return secimler[0].get("Message", {}).get("Content", "[Yuanbao]: BoÅŸ yanÄ±t")
    return f"[Yuanbao]: {yanit}"


def metin_gonullu(metin: str) -> str:
    """Metin duygu analizi (Ã‡ince NLP iÅŸ akÄ±ÅŸlarÄ± için).

    Args:
        metin: Analiz edilecek metin

    Returns:
        Duygu etiketi ve güven skoru
    """
    yanit = hunyuan_sohbet(
        f"Bu metnin duygusunu tek kelimeyle belirt (olumlu/olumsuz/nötr) ve açÄ±kla:\n{metin}",
        sistem="Sen metin analizi uzmanÄ±sÄ±n. KÄ±sa ve net cevap ver.",
    )
    return yanit


def ceviri(metin: str, hedef_dil: str = "Türkçe") -> str:
    """Hunyuan ile metin çeviri.

    Args:
        metin:     Ã‡evrilecek metin
        hedef_dil: Hedef dil adÄ± (Türkçe, Ä°ngilizce, Ã‡ince, vb.)

    Returns:
        Ã‡eviri metni
    """
    return hunyuan_sohbet(
        f"Åunu {hedef_dil}'ye çevir, sadece çeviriyi ver:\n{metin}",
        sistem="Sen profesyonel bir çevirmensin.",
    )


def motor_kaydet(motor):
    """Yuanbao araçlarÄ±nÄ± motora kaydet."""
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return

    motor._plugin_arac_kaydet(
        "YUANBAO_SOHBET",
        lambda mesaj, model="hunyuan-lite": hunyuan_sohbet(mesaj, model=model),
        "Tencent Hunyuan modeline soru sor",
    )
    motor._plugin_arac_kaydet(
        "YUANBAO_CEVIRI",
        lambda metin, hedef_dil="Türkçe": ceviri(metin, hedef_dil),
        "Tencent Hunyuan ile metin çevir",
    )
    motor._plugin_arac_kaydet(
        "YUANBAO_DUYGU",
        lambda metin: metin_gonullu(metin),
        "Metinde duygu analizi yap",
    )


if __name__ == "__main__":
    print(f"App ID: {'âœ“' if YUANBAO_APP_ID else 'âœ—'}")
    if YUANBAO_APP_ID and YUANBAO_SECRET_KEY:
        print(hunyuan_sohbet("Merhaba, nasÄ±lsÄ±n?"))
