# -*- coding: utf-8 -*-
"""gateway/platforms/feishu_comment.py — Feishu Dokuman Yorumlari.

Feishu API v4 ile dokumanlara yorum ekleme, listeleme, silme.
"""

import os
import json
import logging

try:
    import requests
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

logger = logging.getLogger(__name__)

_BASE_URL = "https://open.feishu.cn/open-apis"


def _get_tenant_token() -> str:
    """Feishu tenant access token al (app_id + app_secret ile)."""
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


def send_message(hedef: str, mesaj: str, doc_token: str = None, **kwargs) -> dict:
    """Feishu dokumanina yorum ekler.

    Args:
        hedef: Yorumu ekleyen kullanici ID'si
        mesaj: Yorum metni
        doc_token: Dokuman token'i (opsiyonel, env'den de okunabilir)

    Returns:
        dict: {"durum": "basarili", ...} veya {"durum": "hata", "hata": ...}
    """
    if not _REQUESTS_OK:
        return {"durum": "hata", "hata": "requests kutuphanesi yok."}

    token = os.environ.get("FEISHU_TOKEN", "")
    if not token:
        token = _get_tenant_token()
    if not token:
        return {"durum": "hata", "hata": "FEISHU_TOKEN ayarlanmamis."}

    doc = doc_token or os.environ.get("FEISHU_DOC_TOKEN", "")
    if not doc:
        return {"durum": "hata", "hata": "doc_token gerekli (parametre veya FEISHU_DOC_TOKEN)."}

    try:
        r = requests.post(
            f"{_BASE_URL}/docx/v1/documents/{doc}/comments",
            json={
                "content": json.dumps({
                    "text": mesaj[:5000],
                    "type": "text",
                }, ensure_ascii=False),
            },
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=utf-8",
            },
            timeout=10,
        )
        data = r.json()
        code = data.get("code", -1)
        if code == 0:
            return {"durum": "basarili", "comment_id": data.get("data", {}).get("comment_id", "")}
        return {"durum": "hata", "hata": f"API hatasi {code}: {data.get('msg', '')}"}
    except Exception as e:
        return {"durum": "hata", "hata": str(e)}


def yorumlari_listele(doc_token: str, **kwargs) -> dict:
    """Dokumandaki yorumlari listeler."""
    if not _REQUESTS_OK:
        return {"durum": "hata", "hata": "requests kutuphanesi yok."}

    token = os.environ.get("FEISHU_TOKEN", "") or _get_tenant_token()
    if not token:
        return {"durum": "hata", "hata": "Token alinamadi."}

    try:
        r = requests.get(
            f"{_BASE_URL}/docx/v1/documents/{doc_token}/comments",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        data = r.json()
        if data.get("code") == 0:
            return {"durum": "basarili", "yorumlar": data.get("data", {}).get("items", [])}
        return {"durum": "hata", "hata": f"API hatasi: {data}"}
    except Exception as e:
        return {"durum": "hata", "hata": str(e)}


def yorum_sil(doc_token: str, comment_id: str, **kwargs) -> dict:
    """Dokumandaki bir yorumu siler."""
    if not _REQUESTS_OK:
        return {"durum": "hata", "hata": "requests kutuphanesi yok."}

    token = os.environ.get("FEISHU_TOKEN", "") or _get_tenant_token()
    if not token:
        return {"durum": "hata", "hata": "Token alinamadi."}

    try:
        r = requests.delete(
            f"{_BASE_URL}/docx/v1/documents/{doc_token}/comments/{comment_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        data = r.json()
        if data.get("code") == 0:
            return {"durum": "basarili"}
        return {"durum": "hata", "hata": f"API hatasi: {data}"}
    except Exception as e:
        return {"durum": "hata", "hata": str(e)}


def ping() -> bool:
    """Baglantiyi kontrol eder."""
    token = os.environ.get("FEISHU_TOKEN", "") or _get_tenant_token()
    return bool(token)
