"""
ReYMeN Gateway — SMS (Twilio) platform adapter.

Twilio REST API uzerinden SMS mesaji gonderir.
Gelen mesaj destegi yoktur (yalnizca cikis yonlu).

Yapilandirma (ortam degiskenleri):
  - TWILIO_ACCOUNT_SID     — Twilio Account SID (zorunlu)
  - TWILIO_AUTH_TOKEN      — Twilio Auth Token (zorunlu)
  - TWILIO_FROM_NUMBER     — Gonderen telefon numarasi (zorunlu, E.164 formatinda)
"""

import asyncio
import base64
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


def check_twilio_requirements() -> bool:
    """Check if httpx is available."""
    return HTTPX_AVAILABLE


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


def _env_required(key: str) -> str:
    value = _env(key)
    if not value:
        raise EnvironmentError(f"[SMS] Eksik yapilandirma: {key}")
    return value


# ---------------------------------------------------------------------------
# Twilio API sabitleri
# ---------------------------------------------------------------------------

_TWILIO_API_BASE = "https://api.twilio.com/2010-04-01"
_TWILIO_MESSAGES_ENDPOINT = "/Accounts/{account_sid}/Messages.json"

# Twilio SMS mesaj limiti (tek mesajda 1600 karakter, Go language API docs'a gore)
# Ancak 160 karakterden uzun mesajlar birden fazla segment olarak gonderilir.
# Pratik limit: 1600 karakter (Twilio'nun izin verdigi maksimum)
MAX_MESSAGE_LENGTH = 1600


# ---------------------------------------------------------------------------
# SMS Adapter
# ---------------------------------------------------------------------------


class SMSAdapter(BasePlatformAdapter):
    """
    SMS platform adapter (Twilio).

    Twilio REST API uzerinden SMS mesaji gonderir.
    Yalnizca cikis yonludur (outbound-only); gelen SMS destegi yoktur.
    """

    MAX_MESSAGE_LENGTH = MAX_MESSAGE_LENGTH
    supports_code_blocks = False
    typed_command_prefix = "/"

    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform.SMS)

        # Ortam degiskenlerinden Twilio yapilandirmasi
        self._account_sid: str = _env("TWILIO_ACCOUNT_SID", config.token or "")
        self._auth_token: str = _env("TWILIO_AUTH_TOKEN", config.api_key or "")
        self._from_number: str = _env(
            "TWILIO_FROM_NUMBER",
            config.extra.get("from_number", config.extra.get("phone_number", "")),
        )

        self._client: Optional[httpx.AsyncClient] = None

    # ------------------------------------------------------------------
    # HTTP istemci yonetimi
    # ------------------------------------------------------------------

    async def _get_client(self) -> httpx.AsyncClient:
        """Lazy-init httpx AsyncClient with Twilio basic auth."""
        if self._client is None or self._client.is_closed:
            auth_header = self._build_basic_auth()
            self._client = httpx.AsyncClient(
                base_url=_TWILIO_API_BASE,
                headers={
                    "Authorization": auth_header,
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "ReYMeN-Gateway/1.0",
                },
                timeout=30.0,
            )
        return self._client

    async def _close_client(self) -> None:
        """Close the httpx client if it was created."""
        if self._client is not None:
            try:
                await self._client.aclose()
            except Exception as _e:
                log.warning(f"[src.gateways.platforms.sms] Exception at L131")
                pass
            self._client = None

    def _build_basic_auth(self) -> str:
        """Twilio Basic Auth header'ini olustur."""
        credentials = f"{self._account_sid}:{self._auth_token}"
        encoded = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        return f"Basic {encoded}"

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> bool:
        """Twilio API baglantisini baslat.

        Yapilandirma degiskenlerini dogrular ve HTTP istemcisini hazirlar.
        Twilio API'ye gercek bir baglanti yapilmaz (REST tabanli).
        """
        if not HTTPX_AVAILABLE:
            logger.error(
                "[SMS] httpx kutuphanesi bulunamadi. Kurulum: pip install httpx"
            )
            return False

        # Zorunlu degiskenleri dogrula
        missing = []
        if not self._account_sid:
            missing.append("TWILIO_ACCOUNT_SID")
        if not self._auth_token:
            missing.append("TWILIO_AUTH_TOKEN")
        if not self._from_number:
            missing.append("TWILIO_FROM_NUMBER")

        if missing:
            logger.error(
                "[SMS] Eksik yapilandirma degiskenleri: %s",
                ", ".join(missing),
            )
            return False

        # HTTP istemcisini hazirla (opsiyonel: Twilio API'ye dogrulama istegi)
        try:
            client = await self._get_client()

            # Twilio API'nin erisilebilir oldugunu dogrula (GET account resource)
            resp = await client.get(
                f"/Accounts/{self._account_sid}.json",
            )
            if resp.status_code == 200:
                account_data = resp.json()
                account_name = account_data.get("friendly_name", "N/A")
                logger.info(
                    "[SMS] Twilio API baglantisi basarili: %s (status: %s)",
                    account_name,
                    account_data.get("status", "active"),
                )
            elif resp.status_code == 401:
                logger.error(
                    "[SMS] Twilio API yetkisiz — TWILIO_ACCOUNT_SID veya TWILIO_AUTH_TOKEN gecersiz."
                )
                return False
            else:
                logger.warning(
                    "[SMS] Twilio API yaniti: HTTP %d — %s",
                    resp.status_code,
                    resp.text[:200],
                )

        except httpx.ConnectError as e:
            logger.warning("[SMS] Twilio API baglantisi basarisiz: %s", e)
            # Devam et — runtime'da mesaj gonderiminde tekrar dene
        except Exception as e:
            logger.warning("[SMS] Twilio API dogrulama hatasi: %s", e)

        logger.info("[SMS] Hazir (Twilio REST API).")
        return True

    async def stop(self):
        """Twilio REST API baglantisini durdur."""
        await self._close_client()
        logger.info("[SMS] Kapatildi.")

    # ------------------------------------------------------------------
    # Mesaj Gonderme
    # ------------------------------------------------------------------

    async def send_message(
        self,
        chat_id: str,
        text: str,
        *,
        reply_to: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> SendResult:
        """
        Twilio REST API ile SMS gonderir.

        Parameters
        ----------
        chat_id : str
            Hedef telefon numarasi (E.164 formatinda, orn. +905551234567).
        text : str
            Mesaj icerigi (max 1600 karakter).
        reply_to : str, optional
            Kullanilmaz (SMS protokolunde reply destegi yoktur).
        metadata : dict, optional
            Ek parametreler:
            - ``status_callback``: Teslimat durumu bildirimi icin callback URL
            - ``validity_period``: Mesajin gecerlilik suresi (saniye)
            - ``force_delivery``: Mesaji her zaman gonder (True varsayilan)

        Returns
        -------
        SendResult
        """
        if not HTTPX_AVAILABLE:
            return SendResult(False, error="httpx kurulu degil")

        if not text:
            return SendResult(False, error="Mesaj icerigi bos")

        if not chat_id:
            return SendResult(False, error="Hedef telefon numarasi (chat_id) gerekli")

        if not self._from_number:
            return SendResult(False, error="TWILIO_FROM_NUMBER tanimlanmamis")

        try:
            client = await self._get_client()
            meta = metadata or {}

            # POST body parametreleri
            payload: Dict[str, str] = {
                "To": chat_id,
                "From": self._from_number,
                "Body": text[:MAX_MESSAGE_LENGTH],
            }

            # Opsiyonel parametreler
            status_callback = meta.get("status_callback")
            if status_callback:
                payload["StatusCallback"] = status_callback

            validity_period = meta.get("validity_period")
            if validity_period is not None:
                payload["ValidityPeriod"] = str(validity_period)

            # Twilio Messages API'ye POST
            endpoint = _TWILIO_MESSAGES_ENDPOINT.format(account_sid=self._account_sid)
            resp = await client.post(endpoint, data=payload)

            if resp.is_error:
                error_body = resp.text[:300]
                logger.error(
                    "[SMS] Gonderim hatasi (HTTP %d): %s",
                    resp.status_code,
                    error_body,
                )
                return SendResult(
                    False,
                    error=f"HTTP {resp.status_code}: {error_body}",
                    retryable=resp.status_code in (408, 429, 500, 502, 503, 504),
                )

            response_data = resp.json()
            message_sid = response_data.get("sid", "")
            message_status = response_data.get("status", "unknown")

            logger.info(
                "[SMS] Mesaj gonderildi -> %s | SID: %s | Status: %s",
                chat_id,
                message_sid,
                message_status,
            )

            return SendResult(
                success=True,
                message_id=message_sid,
                raw_response=response_data,
            )

        except httpx.HTTPStatusError as e:
            error_msg = str(e)
            logger.error("[SMS] HTTP hatasi: %s", error_msg)
            return SendResult(False, error=error_msg)
        except httpx.RequestError as e:
            error_msg = f"Baglanti hatasi: {e}"
            logger.error("[SMS] %s", error_msg)
            return SendResult(False, error=error_msg, retryable=True)
        except Exception as e:
            logger.error("[SMS] Gonderim hatasi: %s", e)
            return SendResult(False, error=str(e))

    # ------------------------------------------------------------------
    # Medya gonderimi (SMS desteklemez)
    # ------------------------------------------------------------------

    async def send_typing(self, chat_id: str, metadata: Optional[dict] = None) -> None:
        """SMS typing indicator (no-op — SMS protokolunde yok)."""
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
        """SMS uzerinden resim gonderimi (MMS olarak desteklenebilir).

        Twilio MMS destekliyorsa resim URL'sini mesaj icine ekler.
        MMS kapaliysa sadece caption/resim URL'sini SMS olarak gonderir.
        """
        meta = metadata or {}
        if caption and image_url:
            text = f"{caption}\n{image_url}"
        elif image_url:
            text = image_url
        else:
            text = caption or ""

        if not text:
            return SendResult(False, error="Gonderilecek icerik yok")

        # MMS destegi icin metadata'da media_url parametresi eklenebilir
        return await self.send_message(
            chat_id,
            text,
            reply_to=reply_to,
            metadata={**meta, "_media_url": image_url} if image_url else meta,
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
        """SMS uzerinden dosya gonderimi (sadece dosya adini bildirir).

        SMS protokolu dosya gonderimini desteklemez.
        Dosya adi ve varsa caption SMS olarak gonderilir.
        """
        meta = metadata or {}
        msg = f"Dosya: {file_name or file_path}"
        if caption:
            msg = f"{caption}\n{msg}"

        return await self.send_message(
            chat_id,
            msg,
            reply_to=reply_to,
            metadata=meta,
        )
