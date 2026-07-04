"""
ReYMeN Gateway — Mattermost platform adapter.

Mattermost REST API (http://mattermost.server/api/v4/) uzerinden
mesaj alip gonderir. Thread destegi mevcuttur.

Bagimliliklar:
  - httpx (HTTP istemcisi)

Yapilandirma (ortam degiskenleri):
  - MATTERMOST_URL           — Mattermost sunucu URL (ornek: https://mattermost.example.com)
  - MATTERMOST_TOKEN         — Personal Access Token (PAT)
  - MATTERMOST_TEAM_ID       — Takim ID'si (opsiyonel, ekip bazli islemler icin)
  - MATTERMOST_HOME_CHANNEL  — Varsayilan kanal ID'si
"""

import asyncio
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
    httpx = None  # type: ignore[assignment]  # noqa: F811


def check_mattermost_requirements() -> bool:
    """Check if httpx is available, attempt lazy install if not."""
    global HTTPX_AVAILABLE, httpx
    if HTTPX_AVAILABLE:
        return True
    try:
        from reymen.cron.hermes_stubs import ensure as _lazy_ensure

        _lazy_ensure("platform.mattermost", prompt=False)
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
        raise EnvironmentError(f"[Mattermost] Eksik yapilandirma: {key}")
    return value


# ---------------------------------------------------------------------------
# Mattermost Adapter
# ---------------------------------------------------------------------------


class MattermostAdapter(BasePlatformAdapter):
    """
    Mattermost platform adapter.

    Mattermost REST API (api/v4) ile mesajlasma saglar.
    Personal Access Token ile kimlik dogrulama yapar.
    """

    MAX_MESSAGE_LENGTH = 16383  # Mattermost mesaj limiti (karakter)
    supports_code_blocks = True

    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform.MATTERMOST)
        self._server_url: str = _env("MATTERMOST_URL", "")
        self._token: str = _env("MATTERMOST_TOKEN", config.token or "")
        self._team_id: str = _env("MATTERMOST_TEAM_ID", "")
        self._home_channel: str = _env("MATTERMOST_HOME_CHANNEL", "")

        # Remove trailing slash from server URL
        self._server_url = self._server_url.rstrip("/")

        self._api_base: str = f"{self._server_url}/api/v4"
        self._client: Optional[httpx.AsyncClient] = None

        # Bot/user bilgileri (connect'te doldurulur)
        self._bot_user_id: Optional[str] = None
        self._bot_username: Optional[str] = None

        # Mesaj tekrar korumasi
        self._dedup = MessageDeduplicator()

        # Text batch aggregation
        self._text_batcher = TextBatchAggregator(
            handler=self._handle_incoming_event,
            batch_delay=0.6,
            split_threshold=4000,
        )

    # ── HTTP Istemci Yonetimi ─────────────────────────────────────────

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    "Authorization": f"Bearer {self._token}",
                    "Content-Type": "application/json",
                },
            )
        return self._client

    # ── Baglanti Yonetimi ────────────────────────────────────────────

    async def connect(self) -> bool:
        """
        Mattermost API baglantisini dogrula ve kullanici bilgilerini al.

        GET /api/v4/users/me ile token gecerliligini kontrol eder.
        """
        if not check_mattermost_requirements():
            logger.error("[Mattermost] httpx kurulu degil.")
            return False

        if not self._server_url:
            logger.error("[Mattermost] MATTERMOST_URL eksik.")
            return False

        if not self._token:
            logger.error("[Mattermost] MATTERMOST_TOKEN eksik.")
            return False

        try:
            client = await self._get_client()

            # Kullanici bilgilerini al (token dogrulama)
            resp = await client.get(f"{self._api_base}/users/me")
            resp.raise_for_status()
            user_data = resp.json()

            self._bot_user_id = user_data.get("id", "")
            self._bot_username = user_data.get("username", "")

            logger.info(
                "[Mattermost] Baglanti basarili: %s (%s)",
                self._bot_username,
                self._bot_user_id,
            )

            self._mark_connected()
            return True

        except httpx.HTTPStatusError as e:
            logger.error("[Mattermost] HTTP hatasi: %s", e)
            return False
        except httpx.RequestError as e:
            logger.error("[Mattermost] Baglanti hatasi: %s", e)
            return False
        except Exception as e:
            logger.error("[Mattermost] Beklenmeyen hata: %s", e)
            return False

    async def disconnect(self) -> None:
        """Mattermost HTTP baglantisini kapat."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
            logger.info("[Mattermost] Baglanti kapatildi.")

    # ── Event Isleme ─────────────────────────────────────────────────

    async def process_incoming_webhook(
        self, body: dict, headers: Optional[dict] = None
    ) -> Optional[MessageEvent]:
        """
        Mattermost outgoing webhook / API istegini isle.

        Mattermost, Event API yerine webhook veya polling ile mesaj
        gonderebilir. Bu metod, disardan gelen ham mesajlari MessageEvent'e
        donusturur.
        """
        try:
            # Webhook payload'indan alanlari cikar
            channel_id = body.get("channel_id", "") or body.get("channelId", "")
            user_id = body.get("user_id", "") or body.get("userId", "")
            text = body.get("text", "") or body.get("message", "")
            message_id = body.get("id", "") or body.get("post_id", "")
            thread_id = body.get("root_id", "") or body.get("threadId", "")

            # Bot mesajlarini atla
            if user_id == self._bot_user_id:
                return None

            # MessageType belirle
            msg_type = MessageType.TEXT
            # (Mattermost webhook'ta medya tipi belirlemek icin ek kontroller eklenebilir)

            # Session kaynagi olustur
            from src.gateways.session import SessionSource, build_session_key

            source = SessionSource(
                platform=Platform.MATTERMOST,
                chat_id=channel_id,
                user_id=user_id,
                thread_id=thread_id or None,
                chat_type="group",
            )

            # Tekrar kontrolu
            msg_key = f"{channel_id}_{message_id}"
            if self._dedup.is_duplicate(msg_key):
                return None

            msg_event = MessageEvent(
                text=text or "",
                message_type=msg_type,
                source=source,
                message_id=message_id,
                raw_message=body,
                timestamp=datetime.now(timezone.utc),
            )

            return msg_event

        except Exception as e:
            logger.error("[Mattermost] Webhook isleme hatasi: %s", e)
            return None

    async def _handle_incoming_event(self, event: MessageEvent):
        """Gelen mesaji isleme hattina gonder."""
        try:
            await self._message_handler(event)
        except Exception as e:
            logger.error("[Mattermost] Mesaj isleme hatasi: %s", e)

    # ── Mesaj Gonderme ───────────────────────────────────────────────

    async def send(
        self,
        chat_id: str,
        content: str,
        reply_to: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SendResult:
        """
        Mattermost kanalina mesaj gonder.

        POST /api/v4/posts

        Args:
            chat_id: Kanal ID'si (channel_id)
            content: Mesaj icerigi (Markdown formatinda)
            reply_to: Yanitlanacak mesaj ID'si (thread root)
            metadata: Ek opsiyonlar (thread_id, vb.)

        Returns:
            SendResult
        """
        if not HTTPX_AVAILABLE:
            return SendResult(False, error="httpx kurulu degil")

        channel_id = chat_id or self._home_channel
        if not channel_id:
            return SendResult(False, error="Kanal ID belirtilmemis")

        try:
            client = await self._get_client()

            payload: Dict[str, Any] = {
                "channel_id": channel_id,
                "message": content,
            }

            # Thread yaniti (Mattermost'ta root_id = ustdaki mesaj ID'si)
            thread_id = (metadata or {}).get("thread_id")
            if thread_id:
                payload["root_id"] = thread_id
            elif reply_to:
                payload["root_id"] = reply_to

            resp = await client.post(
                f"{self._api_base}/posts",
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

            return SendResult(
                success=True,
                message_id=data.get("id", ""),
                raw_response=data,
            )

        except httpx.HTTPStatusError as e:
            error_msg = str(e)
            status = e.response.status_code if e.response else 0
            logger.error("[Mattermost] HTTP hatasi (%d): %s", status, error_msg)
            return SendResult(
                False,
                error=error_msg,
                retryable=status in (429, 500, 502, 503, 504),
            )

        except httpx.RequestError as e:
            logger.error("[Mattermost] Istemci hatasi: %s", e)
            return SendResult(False, error=str(e), retryable=True)

        except Exception as e:
            logger.error("[Mattermost] Beklenmeyen gonderim hatasi: %s", e)
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
        Mattermost kanalina mesaj gonder (convenience wrapper).

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
        Mattermost mesajini duzenle.

        PUT /api/v4/posts/{post_id}/patch

        Mattermost, mesaj duzenlemeyi PATCH ile destekler (Sunucu 5.22+).
        Daha eski surumlerde basarisiz olur.
        """
        if not HTTPX_AVAILABLE:
            return SendResult(False, error="httpx kurulu degil")

        try:
            client = await self._get_client()

            payload: Dict[str, Any] = {
                "message": content,
            }

            resp = await client.put(
                f"{self._api_base}/posts/{message_id}/patch",
                json=payload,
            )

            if resp.status_code == 404:
                # Mesaj bulunamadi veya duzenleme desteklenmiyor
                return SendResult(
                    False, error="Mesaj bulunamadi veya duzenleme desteklenmiyor"
                )

            resp.raise_for_status()
            data = resp.json()

            return SendResult(
                success=True,
                message_id=data.get("id", message_id),
                raw_response=data,
            )

        except httpx.HTTPStatusError as e:
            logger.error("[Mattermost] Mesaj duzenleme hatasi: %s", e)
            return SendResult(False, error=str(e))
        except Exception as e:
            logger.error("[Mattermost] Beklenmeyen duzenleme hatasi: %s", e)
            return SendResult(False, error=str(e))

    async def delete_message(
        self,
        chat_id: str,
        message_id: str,
    ) -> bool:
        """
        Mattermost mesajini sil.

        DELETE /api/v4/posts/{post_id}

        Returns:
            True basarili, False basarisiz.
        """
        if not HTTPX_AVAILABLE:
            return False

        try:
            client = await self._get_client()

            resp = await client.delete(
                f"{self._api_base}/posts/{message_id}",
            )
            resp.raise_for_status()
            return True

        except httpx.HTTPStatusError as e:
            logger.error("[Mattermost] Mesaj silme hatasi: %s", e)
            return False
        except Exception as e:
            logger.error("[Mattermost] Beklenmeyen silme hatasi: %s", e)
            return False

    async def send_typing(
        self, chat_id: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Mattermost yaziyor gostergesi (no-op).

        Mattermost REST API, typing indicator icin WebSocket kanali
        gerektirir. REST API uzerinden typing gonderimi desteklenmez.
        """
        pass

    async def send_image(
        self,
        chat_id: str,
        image_url: str,
        caption: Optional[str] = None,
        reply_to: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SendResult:
        """
        Mattermost kanalina resim gonder.

        POST /api/v4/files (once dosya yuklenir, sonra mesaj olarak eklenir)

        Not: Mattermost REST API ile dosya yuklemek icin multipart/form-data
        kullanilir. Dosya once upload edilir, ardindan file_ids ile post
        olusturulur.
        """
        if not HTTPX_AVAILABLE:
            return SendResult(False, error="httpx kurulu degil")

        channel_id = chat_id or self._home_channel
        if not channel_id:
            return SendResult(False, error="Kanal ID belirtilmemis")

        try:
            client = await self._get_client()

            # 1. Once dosyayi yukle
            file_name = Path(image_url).name

            with open(image_url, "rb") as f:
                upload_resp = await client.post(
                    f"{self._api_base}/files",
                    params={"channel_id": channel_id},
                    files={"files": (file_name, f, "application/octet-stream")},
                    headers={
                        "Authorization": f"Bearer {self._token}",
                        # Remove Content-Type so httpx sets multipart boundary
                    },
                )
                upload_resp.raise_for_status()
                upload_data = upload_resp.json()

            file_infos = upload_data.get("file_infos", [])
            if not file_infos:
                return SendResult(False, error="Dosya yuklenemedi")

            file_ids = [f["id"] for f in file_infos if f.get("id")]

            # 2. Mesaji dosya ekleriyle gonder
            thread_id = (metadata or {}).get("thread_id")

            payload: Dict[str, Any] = {
                "channel_id": channel_id,
                "message": caption or "",
                "file_ids": file_ids,
            }

            if thread_id:
                payload["root_id"] = thread_id

            post_resp = await client.post(
                f"{self._api_base}/posts",
                json=payload,
            )
            post_resp.raise_for_status()
            post_data = post_resp.json()

            return SendResult(
                success=True,
                message_id=post_data.get("id", ""),
                raw_response=post_data,
            )

        except httpx.HTTPStatusError as e:
            logger.error("[Mattermost] Resim gonderme hatasi: %s", e)
            return SendResult(False, error=str(e))
        except FileNotFoundError:
            return SendResult(False, error=f"Dosya bulunamadi: {image_url}")
        except Exception as e:
            logger.error("[Mattermost] Beklenmeyen resim hatasi: %s", e)
            return SendResult(False, error=str(e))

    async def send_document(
        self,
        chat_id: str,
        file_path: str,
        caption: Optional[str] = None,
        file_name: Optional[str] = None,
        reply_to: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> SendResult:
        """Mattermost kanalina dosya gonder."""
        return await self.send_image(
            chat_id,
            file_path,
            caption=caption,
            reply_to=reply_to,
            metadata=metadata,
        )

    # ── Kanal/Kullanici Bilgileri ────────────────────────────────────

    async def get_chat_info(self, chat_id: str) -> Dict[str, Any]:
        """
        Kanal bilgilerini getir.

        GET /api/v4/channels/{channel_id}
        """
        if not HTTPX_AVAILABLE or not self._client:
            return {"name": chat_id, "type": "group"}

        try:
            client = await self._get_client()
            resp = await client.get(f"{self._api_base}/channels/{chat_id}")
            resp.raise_for_status()
            data = resp.json()

            return {
                "name": data.get("display_name", data.get("name", chat_id)),
                "type": data.get("type", "group"),
                "id": data.get("id", chat_id),
                "team_id": data.get("team_id", ""),
            }

        except httpx.HTTPStatusError as e:
            logger.warning("[Mattermost] Kanal bilgisi alinamadi: %s", e)
            return {"name": chat_id, "type": "group"}
        except Exception as e:
            logger.warning("[Mattermost] Kanal bilgisi hatasi: %s", e)
            return {"name": chat_id, "type": "group"}

    async def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Kullanici bilgilerini getir.

        GET /api/v4/users/{user_id}
        """
        if not HTTPX_AVAILABLE or not self._client:
            return None

        try:
            client = await self._get_client()
            resp = await client.get(f"{self._api_base}/users/{user_id}")
            resp.raise_for_status()
            data = resp.json()

            return {
                "id": data.get("id", user_id),
                "username": data.get("username", ""),
                "display_name": data.get("nickname", "") or data.get("first_name", ""),
                "email": data.get("email", ""),
            }

        except httpx.HTTPStatusError as e:
            logger.warning("[Mattermost] Kullanici bilgisi alinamadi: %s", e)
            return None
        except Exception as e:
            logger.warning("[Mattermost] Kullanici bilgisi hatasi: %s", e)
            return None

    # ── Channel/Team Yardimcilari ────────────────────────────────────

    async def get_team_channels(
        self, team_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Takimdaki kanallari listele.

        GET /api/v4/teams/{team_id}/channels

        Args:
            team_id: Takim ID'si (belirtilmezse MATTERMOST_TEAM_ID kullanilir)

        Returns:
            Kanal listesi
        """
        tid = team_id or self._team_id
        if not tid:
            logger.warning("[Mattermost] Takim ID belirtilmemis.")
            return []

        if not HTTPX_AVAILABLE or not self._client:
            return []

        try:
            client = await self._get_client()
            resp = await client.get(f"{self._api_base}/teams/{tid}/channels")
            resp.raise_for_status()
            return resp.json()

        except httpx.HTTPStatusError as e:
            logger.error("[Mattermost] Kanal listesi hatasi: %s", e)
            return []
        except Exception as e:
            logger.error("[Mattermost] Beklenmeyen liste hatasi: %s", e)
            return []

    async def create_direct_channel(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Kullaniciyla direkt mesaj kanali olustur.

        POST /api/v4/channels/direct
        Mattermost'ta DM'ler channel_id ile temsil edilir.
        """
        if not self._bot_user_id:
            logger.warning("[Mattermost] Bot kullanici ID'si mevcut degil.")
            return None

        try:
            client = await self._get_client()
            resp = await client.post(
                f"{self._api_base}/channels/direct",
                json=[self._bot_user_id, user_id],
            )
            resp.raise_for_status()
            return resp.json()

        except httpx.HTTPStatusError as e:
            logger.error("[Mattermost] DM kanali olusturma hatasi: %s", e)
            return None
        except Exception as e:
            logger.error("[Mattermost] Beklenmeyen DM hatasi: %s", e)
            return None
