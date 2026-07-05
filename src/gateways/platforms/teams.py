"""
ReYMeN Gateway â€” Microsoft Teams platform adapter.

Microsoft Graph API uzerinden Teams kanallarina mesaj gonderir.

OAuth 2.0 client credentials flow ile yetkilendirme yapar.

Bagimliliklar:
  - httpx (HTTP istemcisi)

Yapilandirma (ortam degiskenleri):
  - TEAMS_TENANT_ID       â€” Microsoft Azure tenant ID (zorunlu)
  - TEAMS_CLIENT_ID       â€” Uygulama (client) ID (zorunlu)
  - TEAMS_CLIENT_SECRET   â€” Uygulama client secret (zorunlu)
  - TEAMS_HOME_CHANNEL    â€” Varsayilan kanal (teamId:channelId, opsiyonel)
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from pathlib import Path as _Path

sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))

from gateways.config import Platform, PlatformConfig
from gateways.platforms.base import (
    BasePlatformAdapter,
    MessageEvent,
    MessageType,
    ProcessingOutcome,
    SendResult,
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
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    httpx = None  # type: ignore[assignment]


def check_teams_requirements() -> bool:
    """Check if httpx is available."""
    return HTTPX_AVAILABLE


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


def _env_required(key: str) -> str:
    value = _env(key)
    if not value:
        raise EnvironmentError(f"[Teams] Eksik yapilandirma: {key}")
    return value


# ---------------------------------------------------------------------------
# Microsoft Teams Adapter
# ---------------------------------------------------------------------------


class TeamsAdapter(BasePlatformAdapter):
    """
    Microsoft Teams platform adapter.

    Microsoft Graph API uzerinden Teams kanallarina mesaj gonderir.
    OAuth 2.0 client credentials flow ile access_token alir.

    ``chat_id`` formati: ``{teamId}:{channelId}``
    Ayirma karakteri ``:`` kullanilir.
    """

    MAX_MESSAGE_LENGTH = 28000  # Teams mesaj limiti (~28K karakter)
    supports_code_blocks = True

    # Microsoft Graph API sabitleri
    _AUTHORITY_BASE = "https://login.microsoftonline.com"
    _GRAPH_BASE = "https://graph.microsoft.com/v1.0"
    _SCOPE = "https://graph.microsoft.com/.default"

    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform.TEAMS)
        self._tenant_id: str = _env_required("TEAMS_TENANT_ID")
        self._client_id: str = _env_required("TEAMS_CLIENT_ID")
        self._client_secret: str = _env_required("TEAMS_CLIENT_SECRET")
        self._home_channel: str = _env("TEAMS_HOME_CHANNEL", "")

        self._client: Optional[httpx.AsyncClient] = None
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

        self._dedup = MessageDeduplicator()

        self._text_batcher = TextBatchAggregator(
            handler=self._handle_incoming_event,
            batch_delay=0.6,
            split_threshold=4000,
        )

    # â”€â”€ OAuth Yardimcisi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    async def _get_access_token(self) -> str:
        """
        Microsoft Graph API icin OAuth 2.0 client credentials access_token al.

        Token suresi dolmadiysa cached token'i don, yoksa yenile.
        """
        now = datetime.now(timezone.utc)

        if self._access_token and self._token_expires_at:
            if (self._token_expires_at - now).total_seconds() > 60:
                return self._access_token

        client = await self._get_client()

        url = f"{self._AUTHORITY_BASE}/{self._tenant_id}/oauth2/v2.0/token"

        data = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "scope": self._SCOPE,
            "grant_type": "client_credentials",
        }

        resp = await client.post(url, data=data)
        resp.raise_for_status()
        token_data = resp.json()

        self._access_token = token_data["access_token"]
        expires_in = token_data.get("expires_in", 3600)
        self._token_expires_at = now.replace(second=(now.second + int(expires_in)) % 60)

        logger.debug("[Teams] Yeni access_token alindi, sure: %s sn", expires_in)
        assert self._access_token is not None
        return self._access_token

    def _parse_chat_id(self, chat_id: str) -> tuple:
        """
        ``chat_id``'den teamId ve channelId'yi ayristir.

        Format: ``{teamId}:{channelId}``
        Ornek: ``abc123:def456``
        """
        parts = chat_id.split(":", 1)
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise ValueError(
                f"[Teams] Gecersiz chat_id formati: {chat_id!r}. "
                f"Beklenen: teamId:channelId"
            )
        return parts[0], parts[1]

    # â”€â”€ Baglanti Yonetimi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def connect(self) -> bool:
        """Teams baglantisini baslat (token dogrulama)."""
        if not HTTPX_AVAILABLE:
            logger.error("[Teams] httpx kurulu degil.")
            return False

        try:
            # Token alinabilirligini dogrula
            await self._get_access_token()
            logger.info("[Teams] Kimlik dogrulama basarili.")
            return True
        except Exception as e:
            logger.error("[Teams] Baglanti hatasi: %s", e)
            return False

    async def disconnect(self) -> None:
        """Teams baglantisini durdur."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
        self._access_token = None
        self._token_expires_at = None

    # â”€â”€ Soyut Metotlar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    async def send(
        self,
        chat_id: str,
        content: str,
        reply_to: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SendResult:
        """Teams kanalina mesaj gonder."""
        if not HTTPX_AVAILABLE:
            return SendResult(False, error="httpx kurulu degil")

        try:
            team_id, channel_id = self._parse_chat_id(chat_id)
            token = await self._get_access_token()
            client = await self._get_client()

            url = (
                f"{self._GRAPH_BASE}/teams/{team_id}" f"/channels/{channel_id}/messages"
            )

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

            payload: Dict[str, Any] = {
                "body": {
                    "contentType": "html",
                    "content": self._text_to_html(content),
                },
            }

            # Thread yaniti (reply)
            if reply_to:
                payload["replyToId"] = reply_to
            elif metadata and metadata.get("thread_id"):
                payload["replyToId"] = metadata["thread_id"]

            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

            return SendResult(
                success=True,
                message_id=data.get("id", ""),
                raw_response=data,
            )

        except httpx.HTTPStatusError as e:
            error_msg = str(e)
            logger.error("[Teams] HTTP hatasi: %s", error_msg)
            return SendResult(False, error=error_msg)
        except Exception as e:
            logger.error("[Teams] Gonderim hatasi: %s", e)
            return SendResult(False, error=str(e))

    async def get_chat_info(self, chat_id: str) -> Dict[str, Any]:
        """Teams kanali bilgisini getir."""
        try:
            team_id, channel_id = self._parse_chat_id(chat_id)
            token = await self._get_access_token()
            client = await self._get_client()

            url = f"{self._GRAPH_BASE}/teams/{team_id}" f"/channels/{channel_id}"

            headers = {
                "Authorization": f"Bearer {token}",
            }

            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()

            return {
                "name": data.get("displayName", ""),
                "type": "channel",
                "team_id": team_id,
                "channel_id": channel_id,
                "description": data.get("description", ""),
                "raw": data,
            }

        except Exception as e:
            logger.error("[Teams] Kanal bilgisi alinamadi: %s", e)
            return {
                "name": chat_id,
                "type": "channel",
                "error": str(e),
            }

    # â”€â”€ Mesaj Gonderme (Ust Katman) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    async def send_message(
        self,
        chat_id: str,
        text: str,
        *,
        reply_to: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> SendResult:
        """Teams kanalina mesaj gonder (send() uzerinden)."""
        return await self.send(
            chat_id or self._home_channel,
            text,
            reply_to=reply_to,
            metadata=metadata,
        )

    async def send_typing(self, chat_id: str, metadata: Optional[dict] = None) -> None:
        """Teams typing indicator (Graph API desteklemez, no-op)."""
        pass

    async def send_image(
        self,
        chat_id: str,
        image_url: str,
        caption: Optional[str] = None,
        reply_to: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SendResult:
        """Teams'e resim gonder (URL olarak)."""
        if caption:
            text = f'{caption}<br><img src="{image_url}" alt="image">'
        else:
            text = f'<img src="{image_url}" alt="image">'
        return await self.send_message(
            chat_id,
            text,
            reply_to=reply_to,
            metadata=metadata,
        )

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
        """Teams'e dosya gonder (dosya yolu olarak)."""
        try:
            from gateways.platforms.base import cache_document_from_bytes

            with open(file_path, "rb") as f:
                data = f.read()

            cached_path = cache_document_from_bytes(data, Path(file_path).suffix)
            msg = f"Dosya: {cached_path}"
            if caption:
                msg = f"{caption}<br>{msg}"

            return await self.send_message(
                chat_id,
                msg,
                reply_to=reply_to,
                metadata=metadata,
            )
        except Exception as e:
            logger.error("[Teams] Dosya gonderme hatasi: %s", e)
            return SendResult(False, error=str(e))

    # â”€â”€ Webhook Isleme â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    async def process_webhook(
        self, body: dict, headers: Optional[dict] = None
    ) -> Optional[MessageEvent]:
        """Teams (Graph API change notification) webhook istegi isle."""
        try:
            # Graph API change notification yapisi
            value = body.get("value", [])
            if not value:
                return None

            notification = value[0]
            resource_data = notification.get("resourceData", notification)
            message_id = resource_data.get("id", "")

            # Gelen mesaj icerigi
            text = resource_data.get("body", {}).get("content", "")
            if not text:
                text = body.get("text", "")

            # Kullanici
            user = resource_data.get("from", {}).get("user", {})
            user_id = user.get("id", "")
            user_name = user.get("displayName", "")

            # Kanal bilgisi (resource URL'den ayristir)
            resource_url = notification.get("resource", "")
            # /teams/{team-id}/channels/{channel-id}/messages/{message-id}
            parts = resource_url.split("/")
            team_id = ""
            channel_id = ""
            for i, part in enumerate(parts):
                if part == "teams" and i + 1 < len(parts):
                    team_id = parts[i + 1]
                elif part == "channels" and i + 1 < len(parts):
                    channel_id = parts[i + 1]

            if not team_id or not channel_id:
                logger.debug("[Teams] Kaynak URL'den kanal bilgisi ayristirilamadi")
                return None

            chat_id_val = f"{team_id}:{channel_id}"

            # Bot mesajlarini atla
            if not user_id:
                return None

            # Session source
            from gateways.session import SessionSource, build_session_key

            source = SessionSource(
                platform=Platform.TEAMS,
                chat_id=chat_id_val,
                user_id=user_id or chat_id_val,
                thread_id=message_id or None,
                chat_type="channel",
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
            msg_key = f"{chat_id_val}_{message_id}"
            if self._dedup.is_duplicate(msg_key):
                return None

            return msg_event

        except Exception as e:
            logger.error("[Teams] Webhook isleme hatasi: %s", e)
            return None

    async def _handle_incoming_event(self, event: MessageEvent):
        """Gelen mesaji isleme hattina gonder."""
        try:
            await self._message_handler(event)
        except Exception as e:
            logger.error("[Teams] Mesaj isleme hatasi: %s", e)

    # â”€â”€ Format Yardimcilari â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    @staticmethod
    def _text_to_html(text: str) -> str:
        """
        Duz metin/markdown icerigini Teams HTML formatina cevir.

        Support temel markdown:
        - **bold** -> <strong>
        - *italic* -> <em>
        - `code` -> <code>
        - ```code block``` -> <pre><code>
        """
        import html as _html
        import re

        # HTML escape - once escape et, sonra markdown donusumlerini uygula
        escaped = _html.escape(text, quote=False)

        # Code blocks (```) -> <pre><code>
        escaped = re.sub(
            r"```(.+?)```",
            r"<pre><code>\1</code></pre>",
            escaped,
            flags=re.DOTALL,
        )

        # Inline code (`) -> <code>
        escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)

        # Bold (**text**) -> <strong>
        escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)

        # Italic (*text*) -> <em>
        escaped = re.sub(r"\*(.+?)\*", r"<em>\1</em>", escaped)

        # Newlines -> <br>
        escaped = escaped.replace("\n", "<br>")

        return escaped

    @staticmethod
    def _html_to_text(html_content: str) -> str:
        """
        Teams HTML mesaj icerigini duz metne cevir.

        Basit bir donusturucu: HTML tag'lerini kaldirir,
        <br> ve </p> -> newline.
        """
        import re

        text = html_content
        # <br>, </p>, </div> -> newline
        text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"</p>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"</div>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<li>", "\n- ", text, flags=re.IGNORECASE)
        text = re.sub(r"</li>", "", text, flags=re.IGNORECASE)

        # Tum kalan HTML tag'lerini kaldir
        text = re.sub(r"<[^>]+>", "", text)

        return text.strip()
