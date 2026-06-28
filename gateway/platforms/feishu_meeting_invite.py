# -*- coding: utf-8 -*-
"""gateway/platforms/feishu_meeting_invite.py — Feishu Toplanti Daveti.

Feishu API v4 ile toplanti olusturma ve katilimci ekleme.
"""

import os
import json
import logging
from datetime import datetime

try:
    import requests
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

logger = logging.getLogger(__name__)

_BASE_URL = "https://open.feishu.cn/open-apis"


def _get_tenant_token() -> str:
    """Feishu tenant access token al."""
    app_id = os.environ.get("FEISHU_APP_ID", "")
    app_secret = os.environ.get("FEISHU_APP_SECRET", "")
    if not app_id or not app_secret:
        return ""
    try:
        r = requests.post(
            f"{_BASE_URL}/auth/v3/tenant_access_token/internal",
            json={"app_id": app_id, "app_secret": app_secret},
            timeout=10,
        )
        data = r.json()
        return data.get("tenant_access_token", "")
    except Exception:
        return ""


def send_message(hedef: str, mesaj: str, baslangic: str = None, bitis: str = None, **kwargs) -> dict:
    """Feishu toplantisi olusturur ve katilimci davet eder.

    Args:
        hedef: Katilimci email adresi veya user ID'si
        mesaj: Toplanti basligi / aciklamasi
        baslangic: Baslangic zamani (ISO 8601, orn: "2026-06-16T14:00:00+08:00")
        bitis: Bitis zamani (ISO 8601)

    Returns:
        dict: {"durum": "basarili", "meeting_id": "..."} veya hata
    """
    if not _REQUESTS_OK:
        return {"durum": "hata", "hata": "requests kutuphanesi yok."}

    token = os.environ.get("FEISHU_TOKEN", "")
    if not token:
        token = _get_tenant_token()
    if not token:
        return {"durum": "hata", "hata": "FEISHU_TOKEN ayarlanmamis."}

    # Varsayilan zaman: simdi + 1 saat, sure 1 saat
    now = datetime.utcnow()
    start_time = baslangic or now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    end_time = bitis or now.replace(hour=(now.hour + 1) % 24).strftime("%Y-%m-%dT%H:%M:%S+08:00")

    katilimcilar = []
    if hedef:
        katilimcilar.append({"user_id": hedef})

    extra_users = kwargs.get("katilimcilar", [])
    if isinstance(extra_users, list):
        for u in extra_users:
            if isinstance(u, dict):
                katilimcilar.append(u)
            else:
                katilimcilar.append({"user_id": str(u)})

    try:
        r = requests.post(
            f"{_BASE_URL}/vc/v1/meetings",
            json={
                "topic": mesaj[:200],
                "start_time": start_time,
                "end_time": end_time,
                "attendees": katilimcilar,
                "meeting_settings": {
                    "auto_record": kwargs.get("kaydet", False),
                    "mute_all": kwargs.get("sustur", False),
                },
            },
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=utf-8",
            },
            timeout=15,
        )
        data = r.json()
        code = data.get("code", -1)
        if code == 0:
            meeting_id = data.get("data", {}).get("meeting", {}).get("id", "")
            return {"durum": "basarili", "meeting_id": meeting_id}
        return {"durum": "hata", "hata": f"API hatasi {code}: {data.get('msg', '')}"}
    except Exception as e:
        return {"durum": "hata", "hata": str(e)}


def ping() -> bool:
    """Baglantiyi kontrol eder."""
    token = os.environ.get("FEISHU_TOKEN", "") or _get_tenant_token()
    return bool(token)
