"""
ReYMeN Gateway — Signal platform adapter.

Signal REST API (signal-cli REST) uzerinden mesaj alip gonderir.
signal-cli-rest-api Docker konteyneri ile calisir.

Yapilandirma (ortam degiskenleri):
  - SIGNAL_URL            — signal-cli REST API URL (ornek: http://localhost:8080)
  - SIGNAL_NUMBER         — Signal numarasi (+905551234567 formatinda)
  - SIGNAL_HOME_CHANNEL   — Varsayilan kanal/hedef numarasi
"""

import asyncio
import logging
import os
import sys
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
    strip_markdown,
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


def check_signal_requirements() -> bool:
    """Check if httpx is available, attempt lazy install if not."""
    global HTTPX_AVAILABLE, httpx
    if HTTPX_AVAILABLE:
        return True
    try:
        from src.reymen.cron.hermes_stubs import ensure as _lazy_ensure
        _lazy_ensure("platform.signal", prompt=False)
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
        raise EnvironmentError(f"[Signal] Eksik yapilandirma: {key}")
    return value


# ---------------------------------------------------------------------------
# Signal Adapter
# ---------------------------------------------------------------------------


class SignalAdapter(BasePlatformAdapter):
    """
    Signal platform adapter.

    signal-cli REST API (http://signal-cli:8080/v2/send) uzerinden
    mesaj gonderir. Webhook tabanli degil — push mesajlasmasi icin
    ayri bir websocket veya polling mekanizmasi gerekebilir.
    Bu adapter yalnizca giden mesaj (send) islemlerini kapsar.
    """

    MAX_MESSAGE_LENGTH = 4096  # signal-cli mesaj limiti (karakter)
    supports_code_blocks = False  # Signal duz metin platformudur

    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform.SIGNAL)

        # Ortam degiskenlerinden yapilandirma
        self._signal_url: str = (
            config.extra.get("http_url")
            or config.extra.get("signal_url")
            or _env("SIGNAL_URL", "")
        )
        self._signal_url = self._signal_url.rstrip("/")

        self._signal_number: str = (
            config.extra.get("number")
            or _env("SIGNAL_NUMBER", "")
        )

        self._home_channel: str = (
            config.extra.get("home_channel")
            or _env("SIGNAL_HOME_CHANNEL", "")
        )

        # HTTP istemcisi
        self._client: Optional[httpx.AsyncClient] = None

        # Mesaj tekrar korumasi
        self._dedup = MessageDeduplicator()

        # Durum
        self._connected = False

    # ------------------------------------------------------------------
    # Property overrides
    # ------------------------------------------------------------------

    @property
    def enforces_own_access_policy(self) -> bool:
        """Signal kendi erisim politikasini uygulamaz, gateway yonetsin."""
        return False

    # ------------------------------------------------------------------
    # Client helpers
    # ------------------------------------------------------------------

    async def _get_client(self) -> httpx.AsyncClient:
        """Return or create the shared httpx client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._signal_url,
                timeout=30.0,
            )
        return self._client

    async def _close_client(self) -> None:
        """Close the httpx client if it was created."""
        if self._client is not None:
            try:
                await self._client.aclose()
            except Exception as _e:
                log.warning(f"[src.gateways.platforms.signal] Exception at L155")
                pass
            self._client = None

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    async def connect(self) -> bool:
        """
        Signal REST API baglantisini baslatir.

        signal-cli REST API'sine bir saglik kontrolu istegi (GET /health)
        gondererek baglantiyi dogrular.
        """
        try:
            if not HTTPX_AVAILABLE:
                logger.error(
                    "[Signal] httpx kutuphanesi bulunamadi. "
                    "Kurulum: pip install httpx"
                )
                self._set_fatal_error(
                    "missing_dependency",
                    "httpx kutuphanesi bulunamadi",
                    retryable=False,
                )
                return False

            if not self._signal_url:
                logger.error(
                    "[Signal] SIGNAL_URL bulunamadi. "
                    "SIGNAL_URL ortam degiskenini ayarlayin "
                    "veya config.yaml'de signal.extra.http_url tanimlayin."
                )
                self._set_fatal_error(
                    "missing_signal_url",
                    "Signal API URL bulunamadi",
                    retryable=False,
                )
                return False

            if not self._signal_number:
                logger.error(
                    "[Signal] SIGNAL_NUMBER bulunamadi. "
                    "SIGNAL_NUMBER ortam degiskenini ayarlayin."
                )
                self._set_fatal_error(
                    "missing_signal_number",
                    "Signal numarasi bulunamadi",
                    retryable=False,
                )
                return False

            # HTTP istemcisini olustur
            client = await self._get_client()

            # Baglantiyi dogrula (GET /health)
            try:
                health_resp = await client.get("/health")
                if health_resp.status_code == 200:
                    logger.info(
                        "[Signal] API baglantisi basarili: %s",
                        self._signal_url,
                    )
                    self._connected = True
                    return True
                else:
                    logger.warning(
                        "[Signal] Saglik kontrolu basarisiz (HTTP %d): %s",
                        health_resp.status_code,
                        health_resp.text[:200],
                    )
                    self._set_fatal_error(
                        "health_check_failed",
                        f"Saglik kontrolu basarisiz (HTTP {health_resp.status_code})",
                        retryable=True,
                    )
                    return False

            except (httpx.ConnectError, httpx.TimeoutException) as e:
                logger.error(
                    "[Signal] API baglantisi basarisiz: %s (%s)",
                    self._signal_url,
                    e,
                )
                self._set_fatal_error(
                    "connection_failed",
                    f"Signal API baglantisi basarisiz: {e}",
                    retryable=True,
                )
                return False

        except Exception as e:
            logger.exception("[Signal] Baglanti hatasi: %s", e)
            self._set_fatal_error(
                "connection_error",
                f"Signal baglanti hatasi: {e}",
                retryable=True,
            )
            return False

    async def disconnect(self) -> None:
        """Signal baglantisini kapat."""
        logger.info("[Signal] Baglanti kapatiliyor...")
        self._connected = False
        await self._close_client()

    @property
    def is_connected(self) -> bool:
        """Return True if the adapter is connected."""
        return self._connected

    # ------------------------------------------------------------------
    # Message sending
    # ------------------------------------------------------------------

    async def send(
        self,
        chat_id: str,
        content: str,
        reply_to: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SendResult:
        """
        Signal numarasina mesaj gonder.

        POST /v2/send

        signal-cli REST API'si su formatta JSON bekler::

            {
                "message": "Merhaba dunya",
                "number": "+905551234567",
                "recipients": ["+905559876543"],
                "text_mode": "normal"
            }

        Args:
            chat_id: Hedef numara (telefon numarasi, +90... formatinda)
            content: Mesaj icerigi
            reply_to: Yanitlanacak mesaj ID'si (opsiyonel, Signal'de
                      QUOTED_MESSAGE ve TIMESTAMP bazli calisir)
            metadata: Ek opsiyonlar

        Returns:
            SendResult
        """
        if not HTTPX_AVAILABLE:
            return SendResult(False, error="httpx kurulu degil")

        recipient = chat_id or self._home_channel
        if not recipient:
            return SendResult(False, error="Hedef numara belirtilmemis")

        try:
            client = await self._get_client()

            # Signal duz metin platformudur — markdown temizle
            plain_text = strip_markdown(content)

            payload: Dict[str, Any] = {
                "message": plain_text,
                "number": self._signal_number,
                "recipients": [recipient],
                "text_mode": "normal",
            }

            logger.debug(
                "[Signal] Mesaj gonderiliyor: recipient=%s, len=%d",
                recipient,
                len(plain_text),
            )

            resp = await client.post(
                "/v2/send",
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

            # signal-cli yaniti genelde soyle doner:
            # {"results": [{"recipient": "+90...", "timestamp": 1234567890}]}
            timestamp = ""
            results = data.get("results") or []
            if results:
                timestamp = str(results[0].get("timestamp", ""))

            return SendResult(
                success=True,
                message_id=timestamp,
                raw_response=data,
            )

        except httpx.HTTPStatusError as e:
            error_msg = str(e)
            status = e.response.status_code if e.response else 0
            logger.error(
                "[Signal] HTTP hatasi (%d): %s",
                status,
                error_msg,
            )
            return SendResult(
                False,
                error=error_msg,
                retryable=status in (429, 500, 502, 503, 504),
            )

        except httpx.RequestError as e:
            logger.error("[Signal] Istemci hatasi: %s", e)
            return SendResult(False, error=str(e), retryable=True)

        except Exception as e:
            logger.error("[Signal] Beklenmeyen gonderim hatasi: %s", e)
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
        Signal numarasina mesaj gonder (convenience wrapper).

        ``send()`` metoduna yonlendirir.
        """
        return await self.send(
            chat_id=chat_id,
            content=text,
            reply_to=reply_to,
            metadata=metadata,
        )
