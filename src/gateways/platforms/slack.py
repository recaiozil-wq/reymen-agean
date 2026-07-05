"""
ReYMeN Gateway — Slack platform adapter.

Slack Web API (Events API + RTM) uzerinden mesaj alip gonderir.

Bagimliliklar:
  - slack-sdk (pip install slack-sdk)
  - httpx (HTTP istemcisi, opsiyonel)

Yapilandirma (ortam degiskenleri):
  - SLACK_BOT_TOKEN          — Slack Bot User OAuth Token (xoxb-...)
  - SLACK_APP_TOKEN          — Slack App-Level Token (xapp-...)
  - SLACK_SIGNING_SECRET     — Slack imza dogrulama anahtari
  - SLACK_HOME_CHANNEL       — Varsayilan kanal/chat_id
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from pathlib import Path as _Path

sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))

from gateways.config import Platform, PlatformConfig
from gateways.platforms.base import (
    BasePlatformAdapter,
    MessageEvent,
    MessageType,
    ProcessingOutcome,
    SendResult,
    cache_image_from_bytes,
    resolve_proxy_url,
)
from gateways.platforms.helpers import (
    MessageDeduplicator,
    TextBatchAggregator,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Bagimlilik kontrolu
# ---------------------------------------------------------------------------

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError

    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False
    WebClient = Any  # type: ignore[assignment]
    SlackApiError = Exception


def check_slack_requirements() -> bool:
    """Check if Slack SDK is available, attempt lazy install if not."""
    global SLACK_AVAILABLE, WebClient, SlackApiError
    if SLACK_AVAILABLE:
        return True
    try:
        from reymen.sistem.reymen_stubs import ensure as _lazy_ensure

        _lazy_ensure("platform.slack", prompt=False)
    except Exception:
        return False
    try:
        from slack_sdk import WebClient as _WC
        from slack_sdk.errors import SlackApiError as _SAE

        WebClient = _WC
        SlackApiError = _SAE
        SLACK_AVAILABLE = True
        return True
    except ImportError:
        return False


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


def _env_required(key: str) -> str:
    value = _env(key)
    if not value:
        raise EnvironmentError(f"[Slack] Eksik yapilandirma: {key}")
    return value


# ---------------------------------------------------------------------------
# Slack Adapter
# ---------------------------------------------------------------------------


class SlackAdapter(BasePlatformAdapter):
    """
    Slack platform adapter.

    Slack Events API ile gercek zamanli mesajlasma saglar.
    Webhook yerine Socket Mode (SocketModeHandler) kullanir.
    """

    MAX_MESSAGE_LENGTH = 40000  # Slack'in mesaj limiti
    supports_code_blocks = True

    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform.SLACK)
        self._bot_token: str = _env("SLACK_BOT_TOKEN", config.token or "")
        self._app_token: str = _env("SLACK_APP_TOKEN", "")
        self._signing_secret: str = _env("SLACK_SIGNING_SECRET", "")
        self._home_channel: str = _env("SLACK_HOME_CHANNEL", "")

        self._client: Optional[WebClient] = None
        self._socket_mode_handler: Optional[Any] = None
        self._bot_user_id: Optional[str] = None
        self._bot_name: Optional[str] = None

        # Mesaj tekrar korumasi
        self._dedup = MessageDeduplicator()

        # Text batch aggregation
        self._text_batcher = TextBatchAggregator(
            handler=self._handle_incoming_event,
            batch_delay=0.6,
            split_threshold=4000,
        )

        # Bot mention pattern
        self._mention_patterns = self._compile_mention_patterns()

    # ── Baglanti Yonetimi ────────────────────────────────────────────

    async def start(self) -> bool:
        """Slack Socket Mode uzerinden baglanti baslat."""
        if not check_slack_requirements():
            logger.error("[Slack] slack-sdk kurulu degil.")
            return False

        if not self._bot_token:
            logger.error("[Slack] SLACK_BOT_TOKEN eksik.")
            return False

        try:
            self._client = WebClient(token=self._bot_token)

            # Bot bilgilerini al
            auth_test = await asyncio.to_thread(self._client.auth_test)
            self._bot_user_id = auth_test.get("user_id", "")
            self._bot_name = auth_test.get("user", "")

            logger.info(
                "[Slack] Baglanti basarili: %s (%s)",
                self._bot_name,
                self._bot_user_id,
            )

            # Socket Mode baslat (app_token gerektirir)
            if self._app_token:
                await self._start_socket_mode()
            else:
                logger.warning(
                    "[Slack] SLACK_APP_TOKEN eksik — polling modunda calisamiyor."
                )

            return True
        except SlackApiError as e:
            logger.error("[Slack] Baglanti hatasi: %s", e)
            return False
        except Exception as e:
            logger.error("[Slack] Beklenmeyen hata: %s", e)
            return False

    async def _start_socket_mode(self):
        """Slack Socket Mode handler baslat."""
        try:
            from slack_sdk.socket_mode import SocketModeClient
            from slack_sdk.socket_mode.request import SocketModeRequest

            self._socket_mode_handler = SocketModeClient(
                app_token=self._app_token,
                web_client=self._client,
            )

            # Mesaj handler'i
            async def _on_message(client, req: SocketModeRequest):
                if req.type == "events_api":
                    payload = req.payload
                    event = payload.get("event", {})
                    event_type = event.get("type", "")

                    if event_type in ("message", "app_mention"):
                        await self._process_slack_event(event, payload)

            self._socket_mode_handler.socket_mode_request_listeners.append(_on_message)

            # Baglanti baslangici (thread'de calisir)
            await asyncio.to_thread(self._socket_mode_handler.connect)
            logger.info("[Slack] Socket Mode aktif.")

        except ImportError:
            logger.warning(
                "[Slack] Socket Mode icin slack_sdk[SocketMode] gerekli. "
                "pip install 'slack-sdk[socket-mode]'"
            )
        except Exception as e:
            logger.error("[Slack] Socket Mode hatasi: %s", e)

    async def stop(self):
        """Slack baglantisini durdur."""
        if self._socket_mode_handler:
            try:
                await asyncio.to_thread(self._socket_mode_handler.close)
                self._socket_mode_handler = None
                logger.info("[Slack] Baglanti kapatildi.")
            except Exception as e:
                logger.warning("[Slack] Baglanti kapatma hatasi: %s", e)

    # ── Mesaj Isleme ─────────────────────────────────────────────────

    async def _process_slack_event(self, event: dict, payload: dict):
        """Slack olayini MessageEvent'e donustur ve isle."""
        event_type = event.get("type", "")
        subtype = event.get("subtype", "")
        channel = event.get("channel", "")
        user = event.get("user", "")
        text = event.get("text", "")
        ts = event.get("ts", "")
        thread_ts = event.get("thread_ts", "")

        # Bot'un kendi mesajlarini atla
        if user == self._bot_user_id:
            return

        # Alt-tip mesajlari atla (channel_join, channel_leave, vs.)
        if subtype and subtype not in ("", "bot_message"):
            if subtype != "bot_message":
                return

        # Tekrar kontrolu
        msg_key = f"{channel}_{ts}"
        if self._dedup.is_duplicate(msg_key):
            return

        # MessageType belirle
        msg_type = MessageType.TEXT
        files = event.get("files", [])
        if files:
            for f in files:
                mime = f.get("mimetype", "")
                if mime.startswith("image/"):
                    msg_type = MessageType.PHOTO
                    break
                elif mime.startswith("video/"):
                    msg_type = MessageType.VIDEO
                    break
                elif mime.startswith("audio/"):
                    msg_type = MessageType.AUDIO
                    break

        # Session kaynagi olustur
        from gateways.session import SessionSource, build_session_key

        source = SessionSource(
            platform=Platform.SLACK,
            chat_id=channel,
            user_id=user,
            thread_id=thread_ts or None,
            chat_type="group",
        )

        msg_event = MessageEvent(
            text=text or "",
            message_type=msg_type,
            source=source,
            message_id=ts,
            raw_message=event,
            timestamp=datetime.now(timezone.utc),
        )

        # Batch aggregation veya dogrudan isle
        if msg_type == MessageType.TEXT and self._text_batcher.is_enabled():
            session_key = build_session_key(source)
            self._text_batcher.enqueue(msg_event, session_key)
        else:
            await self._handle_incoming_event(msg_event)

    async def _handle_incoming_event(self, event: MessageEvent):
        """Gelen mesaji isleme hattina gonder."""
        try:
            await self._message_handler(event)
        except Exception as e:
            logger.error("[Slack] Mesaj isleme hatasi: %s", e)

    # ── Mesaj Gonderme ───────────────────────────────────────────────

    async def send_message(
        self,
        chat_id: str,
        text: str,
        *,
        reply_to: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> SendResult:
        """Slack kanalina mesaj gonder."""
        if not self._client:
            return SendResult(False, error="Slack istemcisi hazir degil")

        try:
            kwargs: Dict[str, Any] = {
                "channel": chat_id,
                "text": text,
            }

            # Thread yaniti
            thread_id = (metadata or {}).get("thread_id")
            if thread_id:
                kwargs["thread_ts"] = thread_id
            elif reply_to:
                kwargs["thread_ts"] = reply_to

            # Markdown destegi
            kwargs["mrkdwn"] = True

            result = await asyncio.to_thread(self._client.chat_postMessage, **kwargs)

            return SendResult(
                success=True,
                message_id=result.get("ts", ""),
                raw_response=result.data,
            )

        except SlackApiError as e:
            error_msg = str(e)
            logger.error("[Slack] Gonderim hatasi: %s", error_msg)
            return SendResult(
                False, error=error_msg, retryable="ratelimited" in error_msg.lower()
            )

        except Exception as e:
            logger.error("[Slack] Beklenmeyen gonderim hatasi: %s", e)
            return SendResult(False, error=str(e))

    async def send_typing(self, chat_id: str, metadata: Optional[dict] = None) -> None:
        """Slack'te yaziyor gostergesi gonder."""
        try:
            # Slack, typing indicator icin chat.postMessage degil,
            # reactions.add veya ephemeral mesaj kullanilabilir
            # Simdilik no-op (Slack Web API typing indicator desteklemez)
            pass
        except Exception as _e:
            log.warning(f"[src.gateways.platforms.slack] Exception at L351")
            pass

    async def send_image(
        self,
        chat_id: str,
        image_path: str,
        *,
        caption: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> SendResult:
        """Slack kanalina resim gonder."""
        if not self._client:
            return SendResult(False, error="Slack istemcisi hazir degil")

        try:
            thread_id = (metadata or {}).get("thread_id")

            with open(image_path, "rb") as f:
                result = await asyncio.to_thread(
                    self._client.files_upload_v2,
                    channel=chat_id,
                    file=f,
                    filename=Path(image_path).name,
                    title=caption or "",
                    thread_ts=thread_id,
                )

            return SendResult(
                success=True,
                message_id=result.get("file", {}).get("id", ""),
            )

        except SlackApiError as e:
            logger.error("[Slack] Resim gonderme hatasi: %s", e)
            return SendResult(False, error=str(e))
        except FileNotFoundError:
            return SendResult(False, error=f"Dosya bulunamadi: {image_path}")
        except Exception as e:
            logger.error("[Slack] Beklenmeyen resim hatasi: %s", e)
            return SendResult(False, error=str(e))

    async def send_document(
        self,
        chat_id: str,
        file_path: str,
        *,
        caption: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> SendResult:
        """Slack kanalina dosya gonder."""
        return await self.send_image(
            chat_id,
            file_path,
            caption=caption,
            metadata=metadata,
        )

    # ── Channel/User Bilgileri ───────────────────────────────────────

    async def get_channel_info(self, channel_id: str) -> Optional[dict]:
        """Kanal bilgilerini getir."""
        if not self._client:
            return None
        try:
            result = await asyncio.to_thread(
                self._client.conversations_info, channel=channel_id
            )
            return result.get("channel", {})
        except SlackApiError:
            return None

    async def get_user_info(self, user_id: str) -> Optional[dict]:
        """Kullanici bilgilerini getir."""
        if not self._client:
            return None
        try:
            result = await asyncio.to_thread(self._client.users_info, user=user_id)
            return result.get("user", {})
        except SlackApiError:
            return None
