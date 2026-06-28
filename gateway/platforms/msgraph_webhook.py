# -*- coding: utf-8 -*-
"""gateway/platforms/msgraph_webhook.py — Microsoft Graph Webhook Abonelikleri.

Webhook olusturma, yenileme, silme.
.env'den MSGRAPH_TENANT_ID, MSGRAPH_CLIENT_ID, MSGRAPH_CLIENT_SECRET okur.
"""

import os
import json
import logging
import datetime

try:
    import requests
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

logger = logging.getLogger(__name__)

_AUTH_URL = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
_GRAPH_URL = "https://graph.microsoft.com/v1.0"


def _get_access_token() -> str:
    """Microsoft Graph icin OAuth2 access token alir.

    .env'den MSGRAPH_TENANT_ID, MSGRAPH_CLIENT_ID, MSGRAPH_CLIENT_SECRET okur.

    Returns:
        str: Erisim tokeni veya bos string
    """
    tenant = os.environ.get("MSGRAPH_TENANT_ID", "")
    client_id = os.environ.get("MSGRAPH_CLIENT_ID", "")
    client_secret = os.environ.get("MSGRAPH_CLIENT_SECRET", "")

    if not tenant or not client_id or not client_secret:
        logger.warning("MSGRAPH_* ortam degiskenleri ayarlanmamis.")
        return ""

    if not _REQUESTS_OK:
        logger.warning("requests kutuphanesi yok.")
        return ""

    try:
        r = requests.post(
            _AUTH_URL.format(tenant=tenant),
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": "https://graph.microsoft.com/.default",
                "grant_type": "client_credentials",
            },
            timeout=15,
        )
        data = r.json()
        token = data.get("access_token", "")
        if not token:
            logger.warning("MSGraph token alinamadi: %s", data.get("error_description", ""))
        return token
    except Exception as e:
        logger.error("MSGraph token hatasi: %s", e)
        return ""


def send_message(hedef: str, mesaj: str, subscription_id: str = None, **kwargs) -> dict:
    """Microsoft Graph uzerinden webhook bildirimi gonderir veya abonelik yonetir.

    Args:
        hedef: Webhook bildirim URL'si (notificationUrl)
        mesaj: Abonelik tipi (orn: "messages", "events", "contacts")
        subscription_id: Mevcut abonelik ID'si (guncelleme/silme icin)

    Keyword Args:
        islem: "olustur" (varsayilan), "yenile", "sil"
        kaynak: Graph kaynagi (orn: "users/{id}/messages")
        sure: Abonelik suresi (dakika, varsayilan: 4230 ~ 3 gun)
        client_state: Opsiyonel dogrulama state'i

    Returns:
        dict: {"durum": "basarili", ...} veya {"durum": "hata", ...}
    """
    if not _REQUESTS_OK:
        return {"durum": "hata", "hata": "requests kutuphanesi yok."}

    token = _get_access_token()
    if not token:
        return {"durum": "hata", "hata": "MSGraph token alinamadi."}

    islem = kwargs.get("islem", "olustur")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        if islem == "sil":
            if not subscription_id:
                return {"durum": "hata", "hata": "silme islemi icin subscription_id gerekli."}
            r = requests.delete(
                f"{_GRAPH_URL}/subscriptions/{subscription_id}",
                headers=headers,
                timeout=10,
            )
            if r.status_code == 204:
                return {"durum": "basarili", "islem": "silindi", "subscription_id": subscription_id}
            return {"durum": "hata", "hata": f"Silme hatasi {r.status_code}: {r.text}"}

        elif islem == "yenile":
            if not subscription_id:
                return {"durum": "hata", "hata": "yenileme islemi icin subscription_id gerekli."}
            sure_dak = kwargs.get("sure", 4230)
            son = (datetime.datetime.utcnow() + datetime.timedelta(minutes=sure_dak)).isoformat() + "Z"
            r = requests.patch(
                f"{_GRAPH_URL}/subscriptions/{subscription_id}",
                json={"expirationDateTime": son},
                headers=headers,
                timeout=10,
            )
            data = r.json()
            if r.status_code == 200:
                return {
                    "durum": "basarili",
                    "islem": "yenilendi",
                    "subscription_id": subscription_id,
                    "son": data.get("expirationDateTime", son),
                }
            return {"durum": "hata", "hata": f"Yenileme hatasi {r.status_code}: {data}"}

        else:  # olustur
            kaynak = kwargs.get("kaynak", mesaj)
            sure_dak = kwargs.get("sure", 4230)
            son = (datetime.datetime.utcnow() + datetime.timedelta(minutes=sure_dak)).isoformat() + "Z"
            body = {
                "changeType": kwargs.get("change_type", "created,updated"),
                "notificationUrl": hedef,
                "resource": kaynak,
                "expirationDateTime": son,
                "clientState": kwargs.get("client_state", "gatewaySecret"),
            }
            r = requests.post(
                f"{_GRAPH_URL}/subscriptions",
                json=body,
                headers=headers,
                timeout=15,
            )
            data = r.json()
            if r.status_code == 201:
                return {
                    "durum": "basarili",
                    "islem": "olusturuldu",
                    "subscription_id": data.get("id", ""),
                    "son": data.get("expirationDateTime", son),
                }
            return {"durum": "hata", "hata": f"Olusturma hatasi {r.status_code}: {data}"}
    except Exception as e:
        return {"durum": "hata", "hata": str(e)}


def ping() -> bool:
    """Microsoft Graph baglantisini kontrol eder.

    Token almayi dener.

    Returns:
        bool: Token basariyla alindiysa True
    """
    token = _get_access_token()
    if not token:
        return False
    # Token gecerli mi kontrol et - basit bir API cagrisi
    try:
        r = requests.get(
            f"{_GRAPH_URL}/subscriptions",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        return r.status_code in (200, 401)  # 401 de token alindigini gosterir (yetki yetersiz olsa da)
    except Exception:
        return False
