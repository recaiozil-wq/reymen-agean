"""
ReYMeN Gateway — Home Assistant platform adapter.

Home Assistant REST API uzerinden mesaj gonderir.
Webhook tabanli degildir; sadece cikis (notification) yonludur.

Yapilandirma (ortam degiskenleri):
  - HASS_TOKEN               — Home Assistant Long-Lived Access Token
  - HASS_HOST                — Home Assistant sunucu adresi (varsayilan: http://homeassistant.local:8123)
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

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
# Bagimlilik kontrolu
# ---------------------------------------------------------------------------

try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    httpx = None  # type: ignore[assignment]


def check_homeassistant_requirements() -> bool:
    """Check if httpx is available."""
    return HTTPX_AVAILABLE


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


# ---------------------------------------------------------------------------
# Home Assistant Adapter
# ---------------------------------------------------------------------------

# Varsayilan Home Assistant REST API base URL
_DEFAULT_HASS_HOST = "http://homeassistant.local:8123"

# API endpointleri
_API_BASE_PATH = "/api"
_API_CONVERSATION_PROCESS = "/api/conversation/process"
_API_SERVICES_PREFIX = "/api/services"
_API_STATES_PREFIX = "/api/states"

# Mesaj limiti (Home Assistant API limiti yok, guvenlik amaciyla konuldu)
MAX_MESSAGE_LENGTH = 32768


class HomeAssistantAdapter(BasePlatformAdapter):
    """
    Home Assistant platform adapter.

    Home Assistant REST API uzerinden notification/conversation mesajlari gonderir.
    Gelen mesaj destegi yoktur (yalnizca cikis yonlu).
    """

    MAX_MESSAGE_LENGTH = MAX_MESSAGE_LENGTH
    supports_code_blocks = False

    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform.HOMEASSISTANT)
        self._token: str = _env("HASS_TOKEN", config.token or "")
        self._host: str = _env(
            "HASS_HOST", config.extra.get("host", _DEFAULT_HASS_HOST)
        )

        self._client: Optional[httpx.AsyncClient] = None

    # ── Baglanti Yonetimi ────────────────────────────────────────────

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def start(self) -> bool:
        """Home Assistant REST API baglantisini baslat."""
        if not HTTPX_AVAILABLE:
            logger.error("[HomeAssistant] httpx kurulu degil.")
            return False

        if not self._token:
            logger.warning(
                "[HomeAssistant] HASS_TOKEN tanimlanmamis; auth basarisiz olabilir."
            )

        # Baglanti dogrulamasi yap (opsiyonel health check)
        try:
            client = await self._get_client()
            headers = self._build_headers()
            resp = await client.get(
                f"{self._host}{_API_BASE_PATH}/",
                headers=headers,
            )
            if resp.status_code == 401:
                logger.error(
                    "[HomeAssistant] API yetkisiz — HASS_TOKEN gecersiz olabilir."
                )
            elif resp.is_error:
                logger.warning(
                    "[HomeAssistant] API yaniti: %s %s",
                    resp.status_code,
                    resp.text[:200],
                )
            else:
                logger.info(
                    "[HomeAssistant] API baglantisi basarili: %s",
                    resp.json().get("message", "OK"),
                )
        except Exception as e:
            logger.warning("[HomeAssistant] API baglanti kontrolu basarisiz: %s", e)
            # Baglanti basarisiz olsa bile devam et (runtime'da tekrar dene)

        logger.info("[HomeAssistant] Hazir (REST API tabanli).")
        return True

    async def stop(self):
        """Home Assistant REST API baglantisini durdur."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    # ── Yardimci Metodlar ────────────────────────────────────────────

    def _build_headers(self) -> Dict[str, str]:
        """API istekleri icin header'lari olustur."""
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

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
        Home Assistant'a mesaj gonderir.

        Iki yontem dener:
        1. ``conversation/process`` — HA'nin built-in conversation agent'ina
           mesaj gonderir (``chat_id`` = ``agent_id`` olarak kullanilir veya
           metadata'dan ``agent_id`` okunur).
        2. ``notify.<service>`` — Bir notify servisine mesaj gonderir
           (``chat_id`` = hedef notify servisi adi, orn. ``notify.mobile_app_iphone``).
        """
        if not HTTPX_AVAILABLE:
            return SendResult(False, error="httpx kurulu degil")

        if not text:
            return SendResult(False, error="Mesaj icerigi bos")

        try:
            client = await self._get_client()
            headers = self._build_headers()

            meta = metadata or {}

            # Yontem 1: conversation/process
            if meta.get("use_conversation", True):
                result = await self._send_via_conversation(
                    client,
                    headers,
                    chat_id,
                    text,
                    meta,
                )
                if result.success:
                    return result
                # Basarisiz olursa notify servisi ile dene (fallback)

            # Yontem 2: notify servisi
            return await self._send_via_notify(
                client,
                headers,
                chat_id,
                text,
                meta,
            )

        except httpx.HTTPStatusError as e:
            error_msg = str(e)
            logger.error("[HomeAssistant] HTTP hatasi: %s", error_msg)
            return SendResult(False, error=error_msg)
        except httpx.RequestError as e:
            error_msg = f"Baglanti hatasi: {e}"
            logger.error("[HomeAssistant] %s", error_msg)
            return SendResult(False, error=error_msg, retryable=True)
        except Exception as e:
            logger.error("[HomeAssistant] Gonderim hatasi: %s", e)
            return SendResult(False, error=str(e))

    async def _send_via_conversation(
        self,
        client: httpx.AsyncClient,
        headers: Dict[str, str],
        chat_id: str,
        text: str,
        metadata: Dict[str, Any],
    ) -> SendResult:
        """
        Home Assistant ``conversation/process`` API ile mesaj gonder.

        ``chat_id`` varsayilan olarak ``agent_id`` olarak kullanilir.
        metadata'da ``agent_id`` da belirtilebilir.
        """
        url = f"{self._host}{_API_CONVERSATION_PROCESS}"

        payload: Dict[str, Any] = {
            "text": text,
        }

        # agent_id belirt
        agent_id = metadata.get("agent_id") or chat_id or "homeassistant"
        if agent_id:
            payload["agent_id"] = agent_id

        # conversation_id (opsiyonel, dialog context icin)
        conv_id = metadata.get("conversation_id")
        if conv_id:
            payload["conversation_id"] = conv_id

        # language (opsiyonel)
        language = metadata.get("language")
        if language:
            payload["language"] = language

        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

        # Basarili conversation yaniti
        response_text = (
            data.get("response", {})
            .get("speech", {})
            .get("plain", {})
            .get("speech", "")
        )
        if response_text:
            logger.debug("[HomeAssistant] Conversation yaniti: %s", response_text[:200])

        return SendResult(
            success=True,
            message_id=data.get("conversation_id", ""),
            raw_response=data,
        )

    async def _send_via_notify(
        self,
        client: httpx.AsyncClient,
        headers: Dict[str, str],
        chat_id: str,
        text: str,
        metadata: Dict[str, Any],
    ) -> SendResult:
        """
        Home Assistant ``notify.<service>`` servisi ile mesaj gonder.

        ``chat_id`` = notify servis adi (orn. ``notify.mobile_app_iphone``,
        ``notify.persistent_notification``).
        """
        # chat_id notify servis adi olarak kullanilir
        service = chat_id or "persistent_notification"
        # "notify." on-eki yoksa ekle
        if not service.startswith("notify."):
            service = f"notify.{service}"

        url = f"{self._host}{_API_SERVICES_PREFIX}/{service.replace('.', '/')}"

        payload: Dict[str, Any] = {
            "message": text,
        }

        # Opsiyonel notify parametreleri
        title = metadata.get("title")
        if title:
            payload["title"] = title

        target = metadata.get("target")
        if target:
            payload["target"] = target

        data_payload = metadata.get("data")
        if data_payload:
            payload["data"] = data_payload

        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()

        return SendResult(
            success=True,
            message_id=service,
            raw_response={"service": service},
        )

    async def send_typing(self, chat_id: str, metadata: Optional[dict] = None) -> None:
        """Home Assistant typing indicator (no-op, REST API desteklemez)."""
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
        """Home Assistant'a resim gonder (notify servisi uzerinden)."""
        meta = metadata or {}
        if caption:
            text = f"{caption}\n{image_url}" if image_url else caption
        else:
            text = image_url or ""

        return await self.send_message(
            chat_id,
            text,
            reply_to=reply_to,
            metadata={**meta, "use_conversation": False},
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
        """Home Assistant'a dosya gonder (notify servisi uzerinden)."""
        meta = metadata or {}
        msg = f"Dosya: {file_path}"
        if caption:
            msg = f"{caption}\n{msg}"

        return await self.send_message(
            chat_id,
            msg,
            reply_to=reply_to,
            metadata={**meta, "use_conversation": False},
        )
