"""
ReYMeN Gateway — Google Chat platform adapter.

Google Chat API (Hangouts Chat) uzerinden mesaj alip gonderir.
Webhook tabanli: Mesaj al -> Beyin'e gonder -> Cevabi Google Chat'e gonder.

Bagimliliklar:
  - httpx (HTTP istemcisi)
  - google-auth (opsiyonel, servis hesabi authentication icin)

Yapilandirma (ortam degiskenleri):
  - GOOGLE_CHAT_BOT_TOKEN     — Bot token / Service Account key
  - GOOGLE_CHAT_SPACE_ID      — Varsayilan alan/chat_id
  - GOOGLE_CHAT_WEBHOOK_URL   — Gelen webhook URL'si
"""

import asyncio
import hashlib
import hmac
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from pathlib import Path as _Path

sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))

from src.gateways.config import Platform, PlatformConfig
from src.gateways.platforms.base import (
    BasePlatformAdapter,
    MessageEvent,
    MessageType,
    ProcessingOutcome,
    SendResult,
    cache_image_from_bytes,
    resolve_proxy_url,
)
from src.gateways.platforms.helpers import (
    MessageDeduplicator,
    TextBatchAggregator,
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


def check_google_chat_requirements() -> bool:
    """Check if httpx is available."""
    return HTTPX_AVAILABLE


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


# ---------------------------------------------------------------------------
# Google Chat Adapter
# ---------------------------------------------------------------------------


class GoogleChatAdapter(BasePlatformAdapter):
    """
    Google Chat platform adapter.

    Google Workspace Chat API ile mesajlasma saglar.
    """

    MAX_MESSAGE_LENGTH = 4096
    supports_code_blocks = True

    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform.GOOGLE_CHAT)
        self._bot_token: str = _env("GOOGLE_CHAT_BOT_TOKEN", config.token or "")
        self._space_id: str = _env("GOOGLE_CHAT_SPACE_ID", "")
        self._webhook_url: str = _env("GOOGLE_CHAT_WEBHOOK_URL", "")

        self._client: Optional[httpx.AsyncClient] = None
        self._api_base: str = "https://chat.googleapis.com/v1"

        self._dedup = MessageDeduplicator()

        self._text_batcher = TextBatchAggregator(
            handler=self._handle_incoming_event,
            batch_delay=0.6,
            split_threshold=4000,
        )

    # ── Baglanti Yonetimi ────────────────────────────────────────────

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def start(self) -> bool:
        """Google Chat baglantisini baslat."""
        if not HTTPX_AVAILABLE:
            logger.error("[GoogleChat] httpx kurulu degil.")
            return False

        logger.info("[GoogleChat] Hazir (webhook tabanli, polling yok).")
        return True

    async def stop(self):
        """Google Chat baglantisini durdur."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    # ── Webhook Isleme ───────────────────────────────────────────────

    async def process_webhook(
        self, body: dict, headers: Optional[dict] = None
    ) -> Optional[MessageEvent]:
        """Google Chat webhook istegi isle."""
        try:
            event_type = body.get("type", "")
            space = body.get("space", {})
            message = body.get("message", body)
            user = message.get("sender", {}).get("name", "")
            text = message.get("text", "")
            message_id = message.get("name", "")
            space_name = space.get("name", "")

            # Event tipleri:
            # ADDED_TO_SPACE, REMOVED_FROM_SPACE, MESSAGE, CARD_CLICKED
            if event_type != "MESSAGE":
                logger.debug("[GoogleChat] Atlanan event: %s", event_type)
                return None

            # Bot mesajlarini atla
            if user and "bots" in user:
                return None

            # Thread ID
            thread = message.get("thread", {})
            thread_id = thread.get("name", "")

            # Session source
            from src.gateways.session import SessionSource, build_session_key

            source = SessionSource(
                platform=Platform.GOOGLE_CHAT,
                chat_id=space_name,
                user_id=user,
                thread_id=thread_id or None,
                chat_type="group",
            )

            msg_event = MessageEvent(
                text=text or "",
                message_type=MessageType.TEXT,
                source=source,
                message_id=message_id,
                raw_message=body,
                timestamp=datetime.now(timezone.utc),
            )

            # Tekrar kontrol
            msg_key = f"{space_name}_{message_id}"
            if self._dedup.is_duplicate(msg_key):
                return None

            return msg_event

        except Exception as e:
            logger.error("[GoogleChat] Webhook isleme hatasi: %s", e)
            return None

    async def _handle_incoming_event(self, event: MessageEvent):
        """Gelen mesaji isleme hattina gonder."""
        try:
            await self._message_handler(event)
        except Exception as e:
            logger.error("[GoogleChat] Mesaj isleme hatasi: %s", e)

    # ── Mesaj Gonderme ───────────────────────────────────────────────

    async def send_message(
        self,
        chat_id: str,
        text: str,
        *,
        reply_to: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> SendResult:
        """Google Chat space'ine mesaj gonder."""
        if not HTTPX_AVAILABLE:
            return SendResult(False, error="httpx kurulu degil")

        try:
            client = await self._get_client()

            # API URL - space adi chat_id olarak kullanilir
            space_name = chat_id or self._space_id
            if not space_name:
                return SendResult(False, error="Space ID belirtilmemis")

            url = f"{self._api_base}/{space_name}/messages"

            headers = {}
            if self._bot_token:
                headers["Authorization"] = f"Bearer {self._bot_token}"

            payload: Dict[str, Any] = {
                "text": text,
            }

            # Thread yaniti
            thread_id = (metadata or {}).get("thread_id")
            if thread_id:
                payload["thread"] = {"name": thread_id}
            elif reply_to:
                payload["thread"] = {"name": reply_to}

            resp = await client.post(url, json=payload, headers=headers or None)
            resp.raise_for_status()
            data = resp.json()

            return SendResult(
                success=True,
                message_id=data.get("name", ""),
                raw_response=data,
            )

        except httpx.HTTPStatusError as e:
            error_msg = str(e)
            logger.error("[GoogleChat] HTTP hatasi: %s", error_msg)
            return SendResult(False, error=error_msg)
        except Exception as e:
            logger.error("[GoogleChat] Gonderim hatasi: %s", e)
            return SendResult(False, error=str(e))

    async def send_typing(self, chat_id: str, metadata: Optional[dict] = None) -> None:
        """Google Chat typing indicator (no-op, API desteklemez)."""
        pass

    async def send_image(
        self,
        chat_id: str,
        image_url: str,
        *,
        caption: Optional[str] = None,
        reply_to: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> SendResult:
        """Google Chat'e resim gonder."""
        return await self.send_message(
            chat_id,
            f"{caption or ''}\n{image_url}" if image_url else (caption or ""),
            reply_to=reply_to,
            metadata=metadata,
        )

    async def send_document(
        self,
        chat_id: str,
        file_path: str,
        *,
        caption: Optional[str] = None,
        file_name: Optional[str] = None,
        reply_to: Optional[str] = None,
        metadata: Optional[dict] = None,
        **kwargs,
    ) -> SendResult:
        """Google Chat'e dosya gonder."""
        try:
            from src.gateways.platforms.base import cache_document_from_bytes

            with open(file_path, "rb") as f:
                data = f.read()

            cached_path = cache_document_from_bytes(data, Path(file_path).suffix)
            msg = f"Dosya: {cached_path}"
            if caption:
                msg = f"{caption}\n{msg}"

            return await self.send_message(
                chat_id,
                msg,
                reply_to=reply_to,
                metadata=metadata,
            )
        except Exception as e:
            logger.error("[GoogleChat] Dosya gonderme hatasi: %s", e)
            return SendResult(False, error=str(e))
