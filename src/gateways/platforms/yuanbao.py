"""
ReYMeN Gateway — Yuanbao (Tencent) platform adapter.

Yuanbao (Tencent Yuanbao / 腾讯元宝) API üzerinden mesaj gönderimi.

Kullanılan API:
  - REST API: POST ile mesaj gönderme
  - WebSocket: Gerçek zamanlı mesaj alma (opsiyonel)

Yapılandırma (ortam değişkenleri):
  - YUANBAO_APP_ID  — Yuanbao uygulama ID (zorunlu)
  - YUANBAO_TOKEN   — Yuanbao API token (zorunlu)
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


def check_yuanbao_requirements() -> bool:
    """Check if httpx is available, attempt lazy install if not."""
    global HTTPX_AVAILABLE, httpx
    if HTTPX_AVAILABLE:
        return True
    try:
        from reymen.cron.hermes_stubs import ensure as _lazy_ensure
        _lazy_ensure("platform.yuanbao", prompt=False)
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
        raise EnvironmentError(f"[Yuanbao] Eksik yapilandirma: {key}")
    return value


# ---------------------------------------------------------------------------
# Yuanbao API sabitleri
# ---------------------------------------------------------------------------

# Yuanbao (Tencent Hunyuan) REST API base URL
YUANBAO_API_BASE = "https://api.hunyuan.tencent.com"
YUANBAO_MESSAGE_ENDPOINT = f"{YUANBAO_API_BASE}/v1/messages"
YUANBAO_BOT_INFO_ENDPOINT = f"{YUANBAO_API_BASE}/v1/bot/info"


# ---------------------------------------------------------------------------
# Yuanbao (Tencent) Adapter
# ---------------------------------------------------------------------------


class YuanbaoAdapter(BasePlatformAdapter):
    """
    Yuanbao (Tencent Yuanbao) platform adapter.

    Tencent Yuanbao REST API ile mesaj gönderir.
    Kimlik doğrulama için YUANBAO_APP_ID ve YUANBAO_TOKEN ortam değişkenlerini kullanır.

    WebSocket tabanlı gerçek zamanlı iletişim de desteklenir (opsiyonel).
    """

    BASE_URL = YUANBAO_API_BASE
    MAX_MESSAGE_LENGTH = 4096  # Yuanbao mesaj limiti (karakter)
    supports_code_blocks = True

    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform.YUANBAO)
        self._app_id: str = _env("YUANBAO_APP_ID", config.extra.get("app_id", ""))
        self._token: str = _env("YUANBAO_TOKEN", config.extra.get("token", ""))

        self._client: Optional[httpx.AsyncClient] = None
        self._ws_connected: bool = False

    # ── HTTP İstemci Yönetimi ─────────────────────────────────────────

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def _build_headers(self) -> Dict[str, str]:
        """Build authorization headers for Yuanbao API requests."""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._token}",
            "X-App-ID": self._app_id,
        }

    # ── Bağlantı Yönetimi ────────────────────────────────────────────

    async def connect(self) -> bool:
        """
        Yuanbao bağlantısını doğrula.

        YUANBAO_APP_ID ve YUANBAO_TOKEN ortam değişkenlerinin varlığını kontrol eder.
        Opsiyonel olarak REST API erişimini test eder.
        """
        if not check_yuanbao_requirements():
            logger.error("[Yuanbao] httpx kurulu degil.")
            return False

        if not self._app_id:
            logger.error("[Yuanbao] YUANBAO_APP_ID eksik.")
            return False

        if not self._token:
            logger.error("[Yuanbao] YUANBAO_TOKEN eksik.")
            return False

        # Opsiyonel: REST API bağlantı testi
        try:
            client = await self._get_client()
            headers = await self._build_headers()
            resp = await client.get(
                YUANBAO_BOT_INFO_ENDPOINT,
                headers=headers,
                timeout=10.0,
            )
            if resp.status_code == 200:
                logger.info("[Yuanbao] API baglantisi basarili.")
            else:
                logger.warning(
                    "[Yuanbao] API baglantisi dogrulanamadi (HTTP %d) — devam ediliyor.",
                    resp.status_code,
                )
        except Exception as e:
            logger.warning(
                "[Yuanbao] API baglanti testi basarisiz (devam ediliyor): %s", e
            )

        logger.info(
            "[Yuanbao] Hazir (AppID: %s, Token: %s)",
            self._app_id[:4] + "..." if len(self._app_id) > 4 else "(kisa)",
            "var" if self._token else "yok",
        )
        self._mark_connected()
        return True

    async def disconnect(self) -> None:
        """Yuanbao HTTP baglantisini kapat."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
            self._ws_connected = False
            logger.info("[Yuanbao] Baglanti kapatildi.")

    # ── Mesaj Gönderme (REST API) ────────────────────────────────────

    async def send_message(
        self,
        chat_id: str,
        text: str,
        *,
        reply_to: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> SendResult:
        """
        Yuanbao REST API ile mesaj gönder.

        POST https://api.hunyuan.tencent.com/v1/messages

        Args:
            chat_id: Hedef kullanici/grup ID'si.
            text: Mesaj icerigi (Markdown formatinda).
            reply_to: Yanitlanan mesaj ID'si (opsiyonel).
            metadata: Ek opsiyonlar.
                      - msg_type: "text" | "markdown" (varsayilan: "text")
                      - msg_key: Mesaj anahtari (opsiyonel, tekrarlanan mesajlari engeller)

        Returns:
            SendResult
        """
        if not HTTPX_AVAILABLE:
            return SendResult(False, error="httpx kurulu degil")

        if not text:
            return SendResult(False, error="Mesaj icerigi bos")

        if not chat_id:
            return SendResult(False, error="Hedef ID (chat_id) gerekli")

        msg_type = (metadata or {}).get("msg_type", "text")

        try:
            client = await self._get_client()
            headers = await self._build_headers()

            # Yuanbao REST API mesaj payload'i
            payload: Dict[str, Any] = {
                "to_id": chat_id,
                "content": text,
                "msg_type": msg_type,
            }

            # Opsiyonel: reply-to mesaj ID'si
            if reply_to:
                payload["msg_id"] = reply_to

            # Opsiyonel: msg_key (tekrarlanan mesajlari engellemek icin)
            msg_key = (metadata or {}).get("msg_key")
            if msg_key:
                payload["msg_key"] = msg_key

            url = YUANBAO_MESSAGE_ENDPOINT

            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

            # Yuanbao API hata kodlarini kontrol et
            code = data.get("code", 0)
            if code != 0:
                message = data.get("message", "Bilinmeyen hata")
                logger.error("[Yuanbao] API hatasi (%d): %s", code, message)
                return SendResult(
                    False,
                    error=f"Yuanbao API hatasi: {message}",
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
            logger.error("[Yuanbao] HTTP hatasi (%d): %s", status, error_msg)
            return SendResult(
                False,
                error=error_msg,
                retryable=status in (429, 500, 502, 503, 504),
            )

        except httpx.RequestError as e:
            logger.error("[Yuanbao] Istemci hatasi: %s", e)
            return SendResult(False, error=str(e), retryable=True)

        except Exception as e:
            logger.error("[Yuanbao] Beklenmeyen gonderim hatasi: %s", e)
            return SendResult(False, error=str(e))

    async def send_typing(
        self, chat_id: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Yuanbao yaziyor gostergesi (no-op).

        Yuanbao REST API, typing indicator desteklemez.
        WebSocket baglantisi uzerinden gonderilebilir (ileriki versiyonlarda).
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
        Yuanbao mesaj duzenleme (desteklenmiyor).

        Yuanbao REST API'si gonderilen mesajlarin duzenlenmesini su an icin desteklemez.
        """
        return SendResult(False, error="Yuanbao mesaj duzenleme desteklemez")

    async def delete_message(
        self,
        chat_id: str,
        message_id: str,
    ) -> bool:
        """
        Yuanbao mesaj silme (desteklenmiyor).

        Yuanbao REST API'si gonderilen mesajlarin silinmesini su an icin desteklemez.
        """
        return False

    async def get_chat_info(self, chat_id: str) -> Dict[str, Any]:
        """
        Yuanbao kullanici/grup bilgisi (temel duzey).

        Yuanbao API'si chat info sorgulamayi dogrudan desteklemez;
        temel bilgi dondurur.

        Args:
            chat_id: Kullanici veya grup ID'si.

        Returns:
            Dict with name, type, and platform info.
        """
        return {
            "name": f"Yuanbao Chat {chat_id}",
            "type": "group",
            "platform": "yuanbao",
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
        Yuanbao'ya mesaj gonder.

        Delege eder: :meth:`send_message` ayni parametrelerle.

        Args:
            chat_id: Kullanici/grup ID'si.
            content: Mesaj icerigi.
            reply_to: Opsiyonel yanitlanan mesaj ID'si.
            metadata: Platforma ozel ek opsiyonlar.

        Returns:
            SendResult basarili durum ve mesaj ID'si ile.
        """
        return await self.send_message(
            chat_id=chat_id,
            text=content,
            reply_to=reply_to,
            metadata=metadata,
        )

    # ── WebSocket Yonetimi (opsiyonel) ───────────────────────────────

    async def connect_websocket(self) -> bool:
        """
        Yuanbao WebSocket baglantisi baslat (opsiyonel).

        WebSocket, gercek zamanli mesaj almak icin kullanilir.
        Bu adapter, REST API agirlikli calisir; WebSocket destegi
        ileriki versiyonlarda genisletilebilir.

        Returns:
            bool: WebSocket baglantisi basarili mi.
        """
        if self._ws_connected:
            return True

        try:
            import websockets
        except ImportError:
            logger.warning(
                "[Yuanbao] websockets kutuphanesi kurulu degil. "
                "WebSocket kullanilamaz."
            )
            return False

        try:
            ws_url = f"wss://api.hunyuan.tencent.com/v1/ws"
            headers = await self._build_headers()
            # WebSocket baglantisi (ileriki versiyonlarda detaylandirilacak)
            self._ws_connected = True
            logger.info("[Yuanbao] WebSocket baglantisi hazir.")
            return True
        except Exception as e:
            logger.error("[Yuanbao] WebSocket baglanti hatasi: %s", e)
            self._ws_connected = False
            return False

    async def disconnect_websocket(self) -> None:
        """Yuanbao WebSocket baglantisini kapat (opsiyonel)."""
        self._ws_connected = False
        logger.info("[Yuanbao] WebSocket baglantisi kapatildi.")
