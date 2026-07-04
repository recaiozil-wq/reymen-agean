"""
ReYMeN Gateway — Matrix platform adapter.

Matrix client-server REST API (https://spec.matrix.org/v1.12/client-server-api/)
uzerinden mesaj alip gonderir. Thread destegi mevcuttur.

Yapilandirma (ortam degiskenleri):
  - MATRIX_HOMESERVER_URL  — Matrix sunucu URL (ornek: https://matrix.example.com)
  - MATRIX_ACCESS_TOKEN    — Erisim tokeni (access token)
  - MATRIX_HOME_ROOM       — Varsayilan oda ID'si
"""

import asyncio
import logging
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from pathlib import Path as _Path

sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))

from src.gateways.config import Platform, PlatformConfig
from src.gateways.platforms.base import (
    BasePlatformAdapter,
    MessageEvent,
    MessageType,
    ProcessingOutcome,
    SendResult,
)
from src.gateways.platforms.helpers import (
    MessageDeduplicator,
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


def check_matrix_requirements() -> bool:
    """Check if httpx is available, attempt lazy install if not."""
    global HTTPX_AVAILABLE, httpx
    if HTTPX_AVAILABLE:
        return True
    try:
        from src.reymen.cron.hermes_stubs import ensure as _lazy_ensure

        _lazy_ensure("platform.matrix", prompt=False)
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
        raise OSError(f"[Matrix] Eksik yapilandirma: {key}")
    return value


# ---------------------------------------------------------------------------
# Matrix Adapter
# ---------------------------------------------------------------------------


class MatrixAdapter(BasePlatformAdapter):
    """
    Matrix platform adapter.

    Matrix client-server REST API (v3) ile mesajlasma saglar.
    Access token ile kimlik dogrulama yapar.
    """

    MAX_MESSAGE_LENGTH = 65536  # Matrix mesaj limiti (karakter)
    supports_code_blocks = True

    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform.MATRIX)

        # Ortam degiskenlerinden yapilandirma
        self._homeserver_url: str = config.extra.get("homeserver_url") or _env(
            "MATRIX_HOMESERVER_URL", ""
        )
        self._homeserver_url = self._homeserver_url.rstrip("/")

        self._access_token: str = (
            config.extra.get("access_token")
            or config.token
            or _env("MATRIX_ACCESS_TOKEN", "")
        )

        self._home_room: str = config.extra.get("home_room") or _env(
            "MATRIX_HOME_ROOM", ""
        )

        # API temel URL
        self._api_base: str = f"{self._homeserver_url}/_matrix/client/v3"

        # HTTP istemcisi
        self._client: Optional["httpx.AsyncClient"] = None

        # Kullanici bilgileri (connect'te doldurulur)
        self._user_id: Optional[str] = None

        # Mesaj tekrar korumasi
        self._dedup = MessageDeduplicator()

    # ------------------------------------------------------------------
    # Property overrides
    # ------------------------------------------------------------------

    @property
    def enforces_own_access_policy(self) -> bool:
        """Matrix kendi erisim politikasini uygulamaz, gateway yonetsin."""
        return False

    # ------------------------------------------------------------------
    # HTTP Istemci Yonetimi
    # ------------------------------------------------------------------

    async def _get_client(self) -> "httpx.AsyncClient":
        """Get or create the HTTP client with auth headers."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    "Authorization": f"Bearer {self._access_token}",
                    "Content-Type": "application/json",
                },
            )
        return self._client

    async def _close_client(self) -> None:
        """Close the httpx client if it was created."""
        if self._client is not None:
            try:
                await self._client.aclose()
            except Exception as _e:
                log.warning(f"[src.gateways.platforms.matrix] Exception at L160")
                pass
            self._client = None

    # ------------------------------------------------------------------
    # Baglanti Yonetimi
    # ------------------------------------------------------------------

    async def connect(self) -> bool:
        """
        Matrix homeserver baglantisini dogrula ve kullanici bilgilerini al.

        GET /_matrix/client/v3/account/whoami ile token gecerliligini kontrol eder.
        """
        try:
            if not HTTPX_AVAILABLE:
                logger.error("[Matrix] httpx kutuphanesi bulunamadi.")
                self._set_fatal_error(
                    "missing_dependency",
                    "httpx kutuphanesi bulunamadi",
                    retryable=False,
                )
                return False

            if not self._homeserver_url:
                logger.error("[Matrix] MATRIX_HOMESERVER_URL eksik.")
                self._set_fatal_error(
                    "missing_homeserver_url",
                    "Matrix homeserver URL bulunamadi",
                    retryable=False,
                )
                return False

            if not self._access_token:
                logger.error("[Matrix] MATRIX_ACCESS_TOKEN eksik.")
                self._set_fatal_error(
                    "missing_access_token",
                    "Matrix access token bulunamadi",
                    retryable=False,
                )
                return False

            client = await self._get_client()

            # Token dogrulama (GET /account/whoami)
            resp = await client.get(f"{self._api_base}/account/whoami")
            resp.raise_for_status()
            data = resp.json()

            self._user_id = data.get("user_id", "")

            logger.info(
                "[Matrix] Baglanti basarili: %s (%s)",
                self._user_id,
                self._homeserver_url,
            )

            self._mark_connected()
            return True

        except httpx.HTTPStatusError as e:
            status = e.response.status_code if e.response else 0
            logger.error("[Matrix] HTTP hatasi (%d): %s", status, e)
            self._set_fatal_error(
                "auth_failed",
                f"Matrix kimlik dogrulama hatasi (HTTP {status})",
                retryable=status in (429, 500, 502, 503, 504),
            )
            return False
        except httpx.RequestError as e:
            logger.error("[Matrix] Baglanti hatasi: %s", e)
            self._set_fatal_error(
                "connection_failed",
                f"Matrix baglanti hatasi: {e}",
                retryable=True,
            )
            return False
        except Exception as e:
            logger.exception("[Matrix] Beklenmeyen baglanti hatasi: %s", e)
            self._set_fatal_error(
                "connection_error",
                f"Matrix baglanti hatasi: {e}",
                retryable=True,
            )
            return False

    async def disconnect(self) -> None:
        """Matrix baglantisini kapat."""
        logger.info("[Matrix] Baglanti kapatiliyor...")
        await self._close_client()

    # ------------------------------------------------------------------
    # Event Isleme
    # ------------------------------------------------------------------

    async def process_incoming_webhook(
        self, body: dict, headers: Optional[dict] = None
    ) -> Optional[MessageEvent]:
        """
        Matrix webhook / callback istegini isle.

        Matrix, Event API uzerinden gelen mesajlari bu metodla
        MessageEvent'e donusturur.

        Beklenen payload formati (Matrix CS API event):
        {
            "event_id": "$eventid",
            "room_id": "!roomid:server",
            "type": "m.room.message",
            "sender": "@user:server",
            "content": {
                "msgtype": "m.text",
                "body": "Mesaj icerigi",
                "m.relates_to": {
                    "rel_type": "m.thread",
                    "event_id": "$thread_root"
                }
            },
            "origin_server_ts": 1234567890
        }
        """
        try:
            event_type = body.get("type", "")
            if event_type != "m.room.message":
                return None

            room_id = body.get("room_id", "")
            sender = body.get("sender", "")
            event_id = body.get("event_id", "")
            content = body.get("content", {}) or {}

            # Bot mesajlarini atla
            if sender == self._user_id:
                return None

            text = content.get("body", "")
            msgtype = content.get("msgtype", "m.text")

            # Thread bilgisini cikar
            relates_to = content.get("m.relates_to", {}) or {}
            thread_id = None
            if isinstance(relates_to, dict):
                if relates_to.get("rel_type") == "m.thread":
                    thread_id = relates_to.get("event_id")
                elif "m.in_reply_to" in relates_to:
                    in_reply_to = relates_to["m.in_reply_to"]
                    if isinstance(in_reply_to, dict):
                        thread_id = in_reply_to.get("event_id")

            # MessageType belirle
            if msgtype in ("m.image",):
                msg_type = MessageType.PHOTO
            elif msgtype in ("m.file",):
                msg_type = MessageType.DOCUMENT
            elif msgtype in ("m.audio",):
                msg_type = MessageType.AUDIO
            elif msgtype in ("m.video",):
                msg_type = MessageType.VIDEO
            else:
                msg_type = MessageType.TEXT

            # Session kaynagi olustur
            from src.gateways.session import SessionSource, build_session_key

            source = SessionSource(
                platform=Platform.MATRIX,
                chat_id=room_id,
                user_id=sender,
                thread_id=thread_id or None,
                chat_type="group",
            )

            # Tekrar kontrolu
            msg_key = f"{room_id}_{event_id}"
            if self._dedup.is_duplicate(msg_key):
                return None

            msg_event = MessageEvent(
                text=text or "",
                message_type=msg_type,
                source=source,
                message_id=event_id,
                raw_message=body,
                timestamp=(
                    datetime.fromtimestamp(
                        body.get("origin_server_ts", 0) / 1000,
                        tz=timezone.utc,
                    )
                    if body.get("origin_server_ts")
                    else datetime.now(timezone.utc)
                ),
            )

            return msg_event

        except Exception as e:
            logger.error("[Matrix] Webhook isleme hatasi: %s", e)
            return None

    # ------------------------------------------------------------------
    # Mesaj Gonderme
    # ------------------------------------------------------------------

    async def send(
        self,
        chat_id: str,
        content: str,
        reply_to: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SendResult:
        """
        Matrix odasina mesaj gonder.

        POST /_matrix/client/v3/rooms/{roomId}/send/m.room.message

        Args:
            chat_id: Oda ID'si (room_id)
            content: Mesaj icerigi (Markdown/HTML formatinda)
            reply_to: Yanitlanacak mesaj ID'si (thread root)
            metadata: Ek opsiyonlar (thread_id, vb.)

        Returns:
            SendResult
        """
        if not HTTPX_AVAILABLE:
            return SendResult(False, error="httpx kurulu degil")

        room_id = chat_id or self._home_room
        if not room_id:
            return SendResult(False, error="Oda ID belirtilmemis")

        try:
            client = await self._get_client()

            # Mesaj icerigini olustur
            payload: Dict[str, Any] = {
                "msgtype": "m.text",
                "body": content,
            }

            # Thread yaniti — Matrix m.relates_to ile calisir
            # https://spec.matrix.org/v1.12/client-server-api/#forming-relationships-between-events
            relates_to: Dict[str, Any] = {}
            thread_id = (metadata or {}).get("thread_id")

            if thread_id:
                # Thread icinde yanit
                relates_to["rel_type"] = "m.thread"
                relates_to["event_id"] = thread_id
            elif reply_to:
                # Duz yanit (thread baslatmaz, sadece reply)
                relates_to["m.in_reply_to"] = {"event_id": reply_to}

            if relates_to:
                payload["m.relates_to"] = relates_to

            logger.debug(
                "[Matrix] Mesaj gonderiliyor: room=%s, len=%d",
                room_id,
                len(content),
            )

            resp = await client.post(
                f"{self._api_base}/rooms/{room_id}/send/m.room.message",
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

            return SendResult(
                success=True,
                message_id=data.get("event_id", ""),
                raw_response=data,
            )

        except httpx.HTTPStatusError as e:
            error_msg = str(e)
            status = e.response.status_code if e.response else 0
            logger.error(
                "[Matrix] HTTP hatasi (%d): %s",
                status,
                error_msg,
            )
            return SendResult(
                False,
                error=error_msg,
                retryable=status in (429, 500, 502, 503, 504),
            )

        except httpx.RequestError as e:
            logger.error("[Matrix] Istemci hatasi: %s", e)
            return SendResult(False, error=str(e), retryable=True)

        except Exception as e:
            logger.error("[Matrix] Beklenmeyen gonderim hatasi: %s", e)
            return SendResult(False, error=str(e))

    async def send_message(
        self,
        chat_id: str,
        text: str,
        *,
        reply_to: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> SendResult:
        """
        Matrix odasina mesaj gonder (convenience wrapper).

        ``send()`` metoduna yonlendirir.
        """
        return await self.send(
            chat_id=chat_id,
            content=text,
            reply_to=reply_to,
            metadata=metadata,
        )

    async def edit_message(
        self,
        chat_id: str,
        message_id: str,
        content: str,
        *,
        finalize: bool = False,
    ) -> SendResult:
        """
        Matrix mesajini duzenle.

        PUT /_matrix/client/v3/rooms/{roomId}/send/m.room.message/{eventId}

        Matrix'te mesaj duzenleme, yeni bir event gonderip eskisinin
        yerine gecmesiyle yapilir (m.replace relation).
        """
        if not HTTPX_AVAILABLE:
            return SendResult(False, error="httpx kurulu degil")

        room_id = chat_id or self._home_room
        if not room_id:
            return SendResult(False, error="Oda ID belirtilmemis")

        try:
            client = await self._get_client()

            # Matrix'te duzenleme, m.replace relation ile yeni event gonderilir
            # https://spec.matrix.org/v1.12/client-server-api/#event-replacements
            payload: Dict[str, Any] = {
                "msgtype": "m.text",
                "body": f" * {content}",
                "m.new_content": {
                    "msgtype": "m.text",
                    "body": content,
                },
                "m.relates_to": {
                    "rel_type": "m.replace",
                    "event_id": message_id,
                },
            }

            resp = await client.put(
                f"{self._api_base}/rooms/{room_id}/send/m.room.message/{message_id}",
                json=payload,
            )

            if resp.status_code == 404:
                return SendResult(
                    False, error="Mesaj bulunamadi veya duzenleme desteklenmiyor"
                )

            resp.raise_for_status()
            data = resp.json()

            return SendResult(
                success=True,
                message_id=data.get("event_id", message_id),
                raw_response=data,
            )

        except httpx.HTTPStatusError as e:
            logger.error("[Matrix] Mesaj duzenleme hatasi: %s", e)
            return SendResult(False, error=str(e))
        except Exception as e:
            logger.error("[Matrix] Beklenmeyen duzenleme hatasi: %s", e)
            return SendResult(False, error=str(e))

    async def delete_message(
        self,
        chat_id: str,
        message_id: str,
    ) -> bool:
        """
        Matrix mesajini sil (redact).

        PUT /_matrix/client/v3/rooms/{roomId}/redact/{eventId}/{txnId}

        Matrix'te mesaj silme islemi "redact" olarak adlandirilir.
        Redact edilen mesajin icerigi sunucudan kaldirilir.

        Returns:
            True basarili, False basarisiz.
        """
        if not HTTPX_AVAILABLE:
            return False

        room_id = chat_id or self._home_room
        if not room_id:
            return False

        try:
            client = await self._get_client()
            txn_id = str(uuid.uuid4())

            resp = await client.put(
                f"{self._api_base}/rooms/{room_id}/redact/{message_id}/{txn_id}",
            )
            resp.raise_for_status()
            return True

        except httpx.HTTPStatusError as e:
            logger.error("[Matrix] Mesaj silme hatasi: %s", e)
            return False
        except Exception as e:
            logger.error("[Matrix] Beklenmeyen silme hatasi: %s", e)
            return False

    async def send_typing(
        self, chat_id: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Matrix yaziyor gostergesi.

        PUT /_matrix/client/v3/rooms/{roomId}/typing/{userId}

        typing: true baslangic, false bitis icin.
        """
        if not HTTPX_AVAILABLE or not self._user_id:
            return

        room_id = chat_id or self._home_room
        if not room_id:
            return

        try:
            client = await self._get_client()
            await client.put(
                f"{self._api_base}/rooms/{room_id}/typing/{self._user_id}",
                json={"typing": True, "timeout": 12000},
            )
        except Exception as e:
            logger.debug("[Matrix] Typing gostergesi hatasi: %s", e)
