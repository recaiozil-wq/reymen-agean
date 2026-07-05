"""
ReYMeN Gateway — DingTalk platform adapter.

DingTalk Robot Webhook + REST API uzerinden mesaj gonderir.

Kullanilan ozellikler:
  - Robot Webhook: Grup icin custom robot mesaji gonderimi (HMAC-SHA256 imzali)
  - (Opsiyonel) REST API: Uygulama bazli mesaj gonderme (DINGTALK_APP_KEY/APP_SECRET ile)

Yapilandirma (ortam degiskenleri):
  - DINGTALK_WEBHOOK_URL  — Robot webhook URL (ornek: https://oapi.dingtalk.com/robot/send?access_token=xxx)
  - DINGTALK_SECRET       — Robot webhook HMAC imzalama anahtari (opsiyonel)
  - DINGTALK_APP_KEY      — DingTalk uygulama AppKey (opsiyonel, REST API icin)
  - DINGTALK_APP_SECRET   — DingTalk uygulama AppSecret (opsiyonel, REST API icin)
"""

import asyncio
import hmac
import hashlib
import base64
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode, urlparse, urlunparse

from pathlib import Path as _Path

sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))

from gateways.config import Platform, PlatformConfig
from gateways.platforms.base import (
    BasePlatformAdapter,
    MessageEvent,
    MessageType,
    SendResult,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Bagimlilik kontrolu
# ---------------------------------------------------------------------------

try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    httpx = None  # type: ignore[assignment]


def check_dingtalk_requirements() -> bool:
    """Check if httpx is available, attempt lazy install if not."""
    global HTTPX_AVAILABLE, httpx
    if HTTPX_AVAILABLE:
        return True
    try:
        from reymen.sistem.reymen_stubs import ensure as _lazy_ensure

        _lazy_ensure("platform.dingtalk", prompt=False)
    except Exception:
        return False
    try:
        import httpx as _httpx

        httpx = _httpx
        HTTPX_AVAILABLE = True
        return True
    except ImportError:
        return False


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


def _env_required(key: str) -> str:
    value = _env(key)
    if not value:
        raise EnvironmentError(f"[DingTalk] Eksik yapilandirma: {key}")
    return value


# ---------------------------------------------------------------------------
# DingTalk Robot Webhook yardimcilari
# ---------------------------------------------------------------------------


def _sign_webhook_request(timestamp: int, secret: str) -> str:
    """DingTalk Robot webhook HMAC-SHA256 imzasi olustur.

    Args:
        timestamp: Unix epoch milisaniye (int(time.time() * 1000))
        secret: HMAC imzalama anahtari (DINGTALK_SECRET)

    Returns:
        Base64-encoded HMAC-SHA256 imzasi.
    """
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        secret.encode("utf-8"),
        string_to_sign.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    return base64.b64encode(hmac_code).decode("utf-8")


def _build_webhook_url(webhook_url: str, secret: str | None = None) -> str:
    """Webhook URL'sine timestamp ve sign parametrelerini ekle (varsa).

    Args:
        webhook_url: Ham webhook URL (access_token icerir)
        secret: Imzalama anahtari (None ise imza eklenmez)

    Returns:
        Imzali (veya duz) webhook URL.
    """
    if not secret:
        return webhook_url

    timestamp = int(time.time() * 1000)
    sign = _sign_webhook_request(timestamp, secret)

    # Mevcut query parametrelerini koru, timestamp ve sign ekle
    parsed = urlparse(webhook_url)
    query_params = {}
    if parsed.query:
        for part in parsed.query.split("&"):
            if "=" in part:
                k, v = part.split("=", 1)
                query_params[k] = v
    query_params["timestamp"] = str(timestamp)
    query_params["sign"] = sign

    new_query = urlencode(query_params)
    return urlunparse(parsed._replace(query=new_query))


# ---------------------------------------------------------------------------
# DingTalk Adapter
# ---------------------------------------------------------------------------


class DingTalkAdapter(BasePlatformAdapter):
    """
    DingTalk platform adapter.

    DingTalk Robot Webhook ile grup mesaji gonderir.
    HMAC-SHA256 imzalama destegi mevcuttur.
    """

    MAX_MESSAGE_LENGTH = 20000  # DingTalk mesaj limiti (karakter)
    supports_code_blocks = True

    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform.DINGTALK)
        self._webhook_url: str = _env(
            "DINGTALK_WEBHOOK_URL", config.extra.get("webhook_url", "")
        )
        self._secret: str = _env("DINGTALK_SECRET", config.extra.get("secret", ""))
        self._app_key: str = _env("DINGTALK_APP_KEY", config.extra.get("app_key", ""))
        self._app_secret: str = _env(
            "DINGTALK_APP_SECRET", config.extra.get("app_secret", "")
        )

        self._client: Optional[httpx.AsyncClient] = None
        self._access_token: Optional[str] = None  # REST API token (future use)

    # ── HTTP Istemci Yonetimi ─────────────────────────────────────────

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    # ── Baglanti Yonetimi ────────────────────────────────────────────

    async def connect(self) -> bool:
        """
        DingTalk baglantisini dogrula.

        Webhook URL'si varsa baglanti basarili sayilir.
        AppKey/AppSecret varsa REST API token almayi dener (opsiyonel).
        """
        if not check_dingtalk_requirements():
            logger.error("[DingTalk] httpx kurulu degil.")
            return False

        if not self._webhook_url:
            logger.error("[DingTalk] DINGTALK_WEBHOOK_URL eksik.")
            return False

        # Webhook URL formatini dogrula
        if "access_token" not in self._webhook_url:
            logger.warning(
                "[DingTalk] Webhook URL'sinde 'access_token' parametresi bulunamadi. "
                "URL ornegi: https://oapi.dingtalk.com/robot/send?access_token=xxx"
            )

        # Opsiyonel: AppKey/AppSecret ile REST API token al
        if self._app_key and self._app_secret:
            try:
                await self._refresh_access_token()
            except Exception as e:
                logger.warning(
                    "[DingTalk] REST API token alinamadi (devam ediliyor): %s", e
                )

        logger.info(
            "[DingTalk] Hazir (Webhook: %s, Imza: %s, REST API: %s)",
            "var" if self._webhook_url else "yok",
            "var" if self._secret else "yok",
            "var" if self._access_token else "yok",
        )
        self._mark_connected()
        return True

    async def disconnect(self) -> None:
        """DingTalk HTTP baglantisini kapat."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
            logger.info("[DingTalk] Baglanti kapatildi.")

    async def _refresh_access_token(self) -> str:
        """DingTalk REST API access token al (AppKey/AppSecret ile).

        GET https://oapi.dingtalk.com/gettoken?appkey=xxx&appsecret=yyy

        Returns:
            Access token string.

        Raises:
            RuntimeError: AppKey veya AppSecret eksikse ya da API hatasi olursa.
        """
        if not self._app_key or not self._app_secret:
            raise RuntimeError("[DingTalk] AppKey/AppSecret eksik.")

        client = await self._get_client()
        resp = await client.get(
            "https://oapi.dingtalk.com/gettoken",
            params={
                "appkey": self._app_key,
                "appsecret": self._app_secret,
            },
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get("errcode") != 0:
            raise RuntimeError(
                f"[DingTalk] Token hatasi: {data.get('errcode')} - {data.get('errmsg', '')}"
            )

        self._access_token = data.get("access_token", "")
        logger.info("[DingTalk] REST API token alindi.")
        return self._access_token

    # ── Mesaj Gonderme ───────────────────────────────────────────────

    async def send_message(
        self,
        chat_id: str,
        text: str,
        *,
        reply_to: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> SendResult:
        """
        DingTalk Robot webhook'una mesaj gonder.

        POST https://oapi.dingtalk.com/robot/send?access_token=xxx

        Args:
            chat_id: Kullanilmaz (webhook URL'si zaten hedef grubu belirler).
                     Uyumluluk amaciyla parametre olarak bulunur.
            text: Mesaj icerigi (Markdown formatinda).
            reply_to: Kullanilmaz (DingTalk Robot Webhook, thread yaniti
                      desteklemez). Uyumluluk amaciyla bulunur.
            metadata: Ek opsiyonlar (msg_type: "text" | "markdown" (varsayilan: text))

        Returns:
            SendResult
        """
        if not HTTPX_AVAILABLE:
            return SendResult(False, error="httpx kurulu degil")

        if not text:
            return SendResult(False, error="Mesaj icerigi bos")

        if not self._webhook_url:
            return SendResult(False, error="DINGTALK_WEBHOOK_URL tanimlanmamis")

        msg_type = (metadata or {}).get("msg_type", "text")

        try:
            client = await self._get_client()

            # Mesaj payload'ini olustur
            payload: Dict[str, Any]
            at_info: Dict[str, Any] = {}

            # Metadata'dan @ mention bilgilerini al
            at_mobiles = (metadata or {}).get("at_mobiles", [])
            at_user_ids = (metadata or {}).get("at_user_ids", [])
            is_at_all = (metadata or {}).get("is_at_all", False)

            if at_mobiles:
                at_info["atMobiles"] = at_mobiles
            if at_user_ids:
                at_info["atUserIds"] = at_user_ids
            if is_at_all:
                at_info["isAtAll"] = True

            if msg_type == "markdown":
                # Markdown mesaji
                title = (metadata or {}).get("title", "ReYMeN")
                payload = {
                    "msgtype": "markdown",
                    "markdown": {
                        "title": title,
                        "text": text,
                    },
                }
                if at_info:
                    payload["at"] = at_info
            else:
                # Duz metin mesaji
                payload = {
                    "msgtype": "text",
                    "text": {
                        "content": text,
                    },
                }
                if at_info:
                    payload["at"] = at_info

            # Webhook URL'sini imzala (varsa)
            webhook_url = _build_webhook_url(self._webhook_url, self._secret)

            resp = await client.post(
                webhook_url,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

            # DingTalk API hata kodlarini kontrol et
            errcode = data.get("errcode", -1)
            if errcode != 0:
                errmsg = data.get("errmsg", "Bilinmeyen hata")
                logger.error("[DingTalk] API hatasi (%d): %s", errcode, errmsg)
                return SendResult(
                    False,
                    error=f"DingTalk API hatasi: {errmsg}",
                    retryable=errcode
                    in (90002, 90006, 90010),  # rate-limit, internal, timeout
                )

            return SendResult(
                success=True,
                message_id=str(data.get("processQueryKey", "")),
                raw_response=data,
            )

        except httpx.HTTPStatusError as e:
            error_msg = str(e)
            status = e.response.status_code if e.response else 0
            logger.error("[DingTalk] HTTP hatasi (%d): %s", status, error_msg)
            return SendResult(
                False,
                error=error_msg,
                retryable=status in (429, 500, 502, 503, 504),
            )

        except httpx.RequestError as e:
            logger.error("[DingTalk] Istemci hatasi: %s", e)
            return SendResult(False, error=str(e), retryable=True)

        except Exception as e:
            logger.error("[DingTalk] Beklenmeyen gonderim hatasi: %s", e)
            return SendResult(False, error=str(e))

    async def send_typing(
        self, chat_id: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        DingTalk yaziyor gostergesi (no-op).

        DingTalk Robot Webhook, typing indicator desteklemez.
        """
        pass

    async def edit_message(
        self,
        chat_id: str,
        message_id: str,
        content: str,
        *,
        finalize: bool = False,
    ) -> SendResult:
        """
        DingTalk mesaj duzenleme (desteklenmiyor).

        DingTalk Robot Webhook uzerinden gonderilen mesajlar
        duzenlenemez.
        """
        return SendResult(
            False, error="DingTalk Robot Webhook mesaj duzenleme desteklemez"
        )

    async def delete_message(
        self,
        chat_id: str,
        message_id: str,
    ) -> bool:
        """
        DingTalk mesaj silme (desteklenmiyor).

        DingTalk Robot Webhook uzerinden gonderilen mesajlar
        silinemez.
        """
        return False
