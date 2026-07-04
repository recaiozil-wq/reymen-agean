"""
ReYMeN Gateway — BlueBubbles platform adapter.

BlueBubbles self-hosted API (https://bluebubbles.app) üzerinden
Apple iMessage mesajlasmasini saglar.

Bagimliliklar:
  - httpx (HTTP istemcisi)

Yapilandirma (ortam degiskenleri):
  - BLUEBUBBLES_URL       — BlueBubbles API base URL (varsayilan:
                            http://localhost:1234/api/v1)
  - BLUEBUBBLES_PASSWORD  — API erisim sifresi (zorunlu)
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Awaitable

from pathlib import Path as _Path

sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))

from src.gateways.config import Platform, PlatformConfig
from src.gateways.platforms.base import (
    BasePlatformAdapter,
    MessageEvent,
    MessageType,
    ProcessingOutcome,
    SendResult,
    resolve_proxy_url,
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


def check_bluebubbles_requirements() -> bool:
    """Check if httpx is available."""
    return HTTPX_AVAILABLE


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


# ---------------------------------------------------------------------------
# BlueBubbles API helper
# ---------------------------------------------------------------------------

_DEFAULT_API_URL = "http://localhost:1234/api/v1"
_TYPING_ON = "true"
_TYPING_OFF = "false"


# ---------------------------------------------------------------------------
# BlueBubbles Adapter
# ---------------------------------------------------------------------------


class BlueBubblesAdapter(BasePlatformAdapter):
    """
    BlueBubbles platform adapter.

    BlueBubbles self-hosted API ile Apple iMessage mesajlasma saglar.
    """

    MAX_MESSAGE_LENGTH = 4000
    supports_code_blocks = True

    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform.BLUEBUBBLES)
        self._api_url: str = _env("BLUEBUBBLES_URL", _DEFAULT_API_URL).rstrip("/")
        self._password: str = _env("BLUEBUBBLES_PASSWORD", "")

        self._client: Optional[httpx.AsyncClient] = None

    # ── HTTP Istemci ──────────────────────────────────────────────────

    async def _get_client(self) -> httpx.AsyncClient:
        """Lazy-init async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def _close_client(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
        self._client = None

    # ── Baglanti Yonetimi ─────────────────────────────────────────────

    async def connect(self) -> bool:
        """
        BlueBubbles API'ye baglanilabilirligi kontrol et.

        ``GET /api/v1/`` saglik kontrolu yaparak sunucunun ayakta
        oldugunu dogrular.
        """
        if not HTTPX_AVAILABLE:
            logger.error("[BlueBubbles] httpx kurulu degil.")
            return False

        if not self._password:
            logger.error(
                "[BlueBubbles] BLUEBUBBLES_PASSWORD ortam degiskeni " "ayarlanmamis."
            )
            return False

        try:
            client = await self._get_client()
            url = f"{self._api_url}/"
            params = {"password": self._password}
            resp = await client.get(url, params=params, timeout=10.0)
            resp.raise_for_status()
            data = resp.json()
            logger.info(
                "[BlueBubbles] API baglantisi basarili: %s",
                data.get("message", "OK"),
            )
            self._mark_connected()
            return True
        except httpx.HTTPError as e:
            logger.error("[BlueBubbles] API baglanti hatasi: %s", e)
            return False
        except Exception as e:
            logger.error("[BlueBubbles] Beklenmeyen baglanti hatasi: %s", e)
            return False

    async def disconnect(self) -> None:
        """BlueBubbles API baglantisini kapat."""
        await self._close_client()
        self._mark_disconnected()
        logger.info("[BlueBubbles] Baglanti kapatildi.")

    # ── Mesaj Gonderme ────────────────────────────────────────────────

    async def send(
        self,
        chat_id: str,
        content: str,
        reply_to: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SendResult:
        """
        ``chat_id`` ile belirtilen iMessage gorusmesine mesaj gonder.

        BlueBubbles API endpoint: ``POST /api/v1/message``

        Args:
            chat_id: Alisverisin GUID'i (iMessage chat identifier).
            content: Gonderilecek mesaj metni.
            reply_to: Opsiyonel, yanitlanan mesajin GUID'i.
            metadata: ``method`` (``"apple"`` / ``"private-api"``) vb.
                      opsiyonel param.

        Returns:
            SendResult.
        """
        if not HTTPX_AVAILABLE:
            return SendResult(success=False, error="httpx kurulu degil")

        if not self._password:
            return SendResult(
                success=False,
                error="BLUEBUBBLES_PASSWORD ayarlanmamis",
            )

        try:
            client = await self._get_client()
            url = f"{self._api_url}/message"

            payload: Dict[str, Any] = {
                "chatGuid": chat_id,
                "text": content,
                "password": self._password,
            }

            if reply_to:
                payload["replyToGuid"] = reply_to
                payload["replyTo"] = reply_to  # some BB versions use this key

            # Opsiyonel metadata: method ("apple" / "private-api")
            method = (metadata or {}).get("method")
            if method:
                payload["method"] = method

            resp = await client.post(url, json=payload, timeout=30.0)
            resp.raise_for_status()
            data = resp.json()

            message_id = data.get("sentMessage", {}).get("guid") or data.get("guid", "")
            return SendResult(
                success=True,
                message_id=str(message_id) if message_id else None,
                raw_response=data,
            )

        except httpx.HTTPStatusError as e:
            error_body = ""
            try:
                error_body = str(e.response.text)
            except Exception as _e:
                log.warning(f"[src.gateways.platforms.bluebubbles] Exception at L223")
                pass
            error_msg = f"HTTP {e.response.status_code}: {error_body or str(e)}"
            logger.error("[BlueBubbles] Gonderim HTTP hatasi: %s", error_msg)
            return SendResult(success=False, error=error_msg)

        except httpx.RequestError as e:
            logger.error("[BlueBubbles] Gonderim baglanti hatasi: %s", e)
            return SendResult(success=False, error=str(e), retryable=True)

        except Exception as e:
            logger.error("[BlueBubbles] Gonderim hatasi: %s", e)
            return SendResult(success=False, error=str(e))

    # ── Typing Indicator ──────────────────────────────────────────────

    async def send_typing(self, chat_id: str, metadata: Optional[dict] = None) -> None:
        """
        iMessage typing indicator gonder.

        BlueBubbles API endpoint: ``POST /api/v1/typing``

        ``metadata`` icinden ``typing`` (bool) degeri okur:
          - ``True`` (varsayilan): yaziyor gosterimi baslat.
          - ``False``: yaziyor gosterimini durdur.
        """
        if not HTTPX_AVAILABLE or not self._password:
            return

        is_typing = True
        if metadata and isinstance(metadata, dict):
            is_typing = metadata.get("typing", True)

        try:
            client = await self._get_client()
            url = f"{self._api_url}/typing"

            payload: Dict[str, Any] = {
                "chatGuid": chat_id,
                "typing": _TYPING_ON if is_typing else _TYPING_OFF,
                "password": self._password,
            }

            resp = await client.post(url, json=payload, timeout=10.0)
            resp.raise_for_status()

        except Exception as e:
            logger.debug("[BlueBubbles] Typing gonderim hatasi (%s): %s", chat_id, e)

    # ── Opsiyonel: Mesaj Silme ────────────────────────────────────────

    async def delete_message(self, chat_id: str, message_id: str) -> bool:
        """
        BlueBubbles API ile mesaj sil.

        Endpoint: ``DELETE /api/v1/message/{guid}``
        """
        if not HTTPX_AVAILABLE or not self._password:
            return False

        try:
            client = await self._get_client()
            url = f"{self._api_url}/message/{message_id}"
            params = {"password": self._password}
            resp = await client.delete(url, params=params, timeout=10.0)
            resp.raise_for_status()
            return True
        except Exception as e:
            logger.debug(
                "[BlueBubbles] Mesaj silme hatasi (%s/%s): %s",
                chat_id,
                message_id,
                e,
            )
            return False

    # ── Opsiyonel: Mesaj Getirme ──────────────────────────────────────

    async def get_messages(
        self,
        chat_id: str,
        limit: int = 50,
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> Optional[List[dict]]:
        """
        Bir gorusmedeki mesajlari getir.

        Endpoint: ``GET /api/v1/chat/messages``
        """
        if not HTTPX_AVAILABLE or not self._password:
            return None

        try:
            client = await self._get_client()
            url = f"{self._api_url}/chat/messages"
            params: Dict[str, Any] = {
                "chatGuid": chat_id,
                "password": self._password,
                "limit": limit,
            }
            if before:
                params["before"] = before
            if after:
                params["after"] = after

            resp = await client.get(url, params=params, timeout=15.0)
            resp.raise_for_status()
            data = resp.json()
            return data.get("messages", [])

        except Exception as e:
            logger.debug("[BlueBubbles] Mesaj getirme hatasi (%s): %s", chat_id, e)
            return None
