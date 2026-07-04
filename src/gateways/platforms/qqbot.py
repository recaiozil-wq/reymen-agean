"""
ReYMeN Gateway — QQ Bot platform adapter.

QQ Bot API (https://api.q.qq.com) üzerinden grup mesajı gönderir.

Kullanılan API:
  - POST /v2/groups/{group_id}/messages — grup mesajı gönderme

Yapılandırma (ortam değişkenleri):
  - QBOT_APP_ID   — QQ Bot uygulama ID (zorunlu)
  - QBOT_TOKEN    — QQ Bot access token (zorunlu)
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from pathlib import Path as _Path

sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))

from src.gateways.config import Platform, PlatformConfig
from src.gateways.platforms.base import (
    BasePlatformAdapter,
    MessageEvent,
    MessageType,
    SendResult,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Bağımlılık kontrolü
# ---------------------------------------------------------------------------

try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    httpx = None  # type: ignore[assignment]


def check_qqbot_requirements() -> bool:
    """Check if httpx is available, attempt lazy install if not."""
    global HTTPX_AVAILABLE, httpx
    if HTTPX_AVAILABLE:
        return True
    try:
        from reymen.cron.hermes_stubs import ensure as _lazy_ensure

        _lazy_ensure("platform.qqbot", prompt=False)
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
        raise EnvironmentError(f"[QQBot] Eksik yapılandırma: {key}")
    return value


# ---------------------------------------------------------------------------
# QQ Bot Adapter
# ---------------------------------------------------------------------------


class QQAdapter(BasePlatformAdapter):
    """
    QQ Bot platform adapter.

    QQ Bot REST API (https://api.q.qq.com) ile grup mesajı gönderir.
    Kimlik doğrulama için QBOT_APP_ID ve QBOT_TOKEN ortam değişkenlerini kullanır.
    """

    BASE_URL = "https://api.q.qq.com"
    MAX_MESSAGE_LENGTH = 2000  # QQ Bot mesaj limiti (karakter)
    supports_code_blocks = True

    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform.QQBOT)
        self._app_id: str = _env("QBOT_APP_ID", config.extra.get("app_id", ""))
        self._token: str = _env("QBOT_TOKEN", config.extra.get("token", ""))

        self._client: Optional[httpx.AsyncClient] = None

    # ── HTTP İstemci Yönetimi ─────────────────────────────────────────

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def _build_headers(self) -> Dict[str, str]:
        """Build authorization headers for QQ Bot API requests."""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._token}",
            "X-APP-ID": self._app_id,
        }

    # ── Bağlantı Yönetimi ────────────────────────────────────────────

    async def connect(self) -> bool:
        """
        QQ Bot bağlantısını doğrula.

        QBOT_APP_ID ve QBOT_TOKEN ortam değişkenlerinin varlığını kontrol eder.
        """
        if not check_qqbot_requirements():
            logger.error("[QQBot] httpx kurulu değil.")
            return False

        if not self._app_id:
            logger.error("[QQBot] QBOT_APP_ID eksik.")
            return False

        if not self._token:
            logger.error("[QQBot] QBOT_TOKEN eksik.")
            return False

        logger.info(
            "[QQBot] Hazir (AppID: %s, Token: %s)",
            self._app_id[:4] + "..." if len(self._app_id) > 4 else "(kisa)",
            "var" if self._token else "yok",
        )
        self._mark_connected()
        return True

    async def disconnect(self) -> None:
        """QQ Bot HTTP bağlantısını kapat."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
            logger.info("[QQBot] Baglanti kapatildi.")

    # ── Mesaj Gönderme ───────────────────────────────────────────────

    async def send_message(
        self,
        chat_id: str,
        text: str,
        *,
        reply_to: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> SendResult:
        """
        QQ Bot API ile grup mesajı gönder.

        POST https://api.q.qq.com/v2/groups/{group_id}/messages

        Args:
            chat_id: Grup ID'si (group_id).
            text: Mesaj içeriği.
            reply_to: Kullanılmaz (QQ Bot API'si reply-to desteklemez).
            metadata: Ek opsiyonlar (msg_type: "text" | "markdown", varsayılan: "text").

        Returns:
            SendResult
        """
        if not HTTPX_AVAILABLE:
            return SendResult(False, error="httpx kurulu degil")

        if not text:
            return SendResult(False, error="Mesaj icerigi bos")

        if not chat_id:
            return SendResult(False, error="Grup ID'si (chat_id) gerekli")

        msg_type = (metadata or {}).get("msg_type", "text")

        try:
            client = await self._get_client()
            headers = await self._build_headers()

            # QQ Bot API mesaj payload'ı
            payload: Dict[str, Any] = {
                "content": text,
                "msg_type": msg_type,
            }

            # Opsiyonel: reply-to mesaj ID'si
            if reply_to:
                payload["msg_id"] = reply_to

            url = f"{self.BASE_URL}/v2/groups/{chat_id}/messages"

            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

            # QQ Bot API hata kodlarını kontrol et
            code = data.get("code", 0)
            if code != 0:
                message = data.get("message", "Bilinmeyen hata")
                logger.error("[QQBot] API hatasi (%d): %s", code, message)
                return SendResult(
                    False,
                    error=f"QQ Bot API hatasi: {message}",
                    retryable=code in (500, 502, 503, 504, 429),
                )

            return SendResult(
                success=True,
                message_id=str(data.get("id", "")),
                raw_response=data,
            )

        except httpx.HTTPStatusError as e:
            error_msg = str(e)
            status = e.response.status_code if e.response else 0
            logger.error("[QQBot] HTTP hatasi (%d): %s", status, error_msg)
            return SendResult(
                False,
                error=error_msg,
                retryable=status in (429, 500, 502, 503, 504),
            )

        except httpx.RequestError as e:
            logger.error("[QQBot] Istemci hatasi: %s", e)
            return SendResult(False, error=str(e), retryable=True)

        except Exception as e:
            logger.error("[QQBot] Beklenmeyen gonderim hatasi: %s", e)
            return SendResult(False, error=str(e))

    async def send_typing(
        self, chat_id: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        QQ Bot yazıyor göstergesi (no-op).

        QQ Bot API, typing indicator desteklemez.
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
        QQ Bot mesaj düzenleme (desteklenmiyor).

        QQ Bot API'si gönderilen mesajların düzenlenmesini desteklemez.
        """
        return SendResult(False, error="QQ Bot mesaj duzenleme desteklemez")

    async def delete_message(
        self,
        chat_id: str,
        message_id: str,
    ) -> bool:
        """
        QQ Bot mesaj silme (desteklenmiyor).

        QQ Bot API'si gönderilen mesajların silinmesini desteklemez.
        """
        return False

    async def get_chat_info(self, chat_id: str) -> Dict[str, Any]:
        """
        QQ Bot grup bilgisi (temel düzey).

        QQ Bot API'si chat info sorgulamayı doğrudan desteklemez;
        temel bilgi döndürür.

        Args:
            chat_id: Grup ID'si.

        Returns:
            Dict with name, type, and platform info.
        """
        return {
            "name": f"QQ Group {chat_id}",
            "type": "group",
            "platform": "qqbot",
        }

    # ── Ortak API (BasePlatformAdapter.send delegasyonu) ─────────────

    async def send(
        self,
        chat_id: str,
        content: str,
        reply_to: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SendResult:
        """
        Send a message to a QQ group.

        Delegates to :meth:`send_message` with the same parameters.

        Args:
            chat_id: Group ID.
            content: Message content.
            reply_to: Optional message ID to reply to.
            metadata: Additional platform-specific options.

        Returns:
            SendResult with success status and message ID.
        """
        return await self.send_message(
            chat_id=chat_id,
            text=content,
            reply_to=reply_to,
            metadata=metadata,
        )
