"""
ReYMeN Gateway — WhatsApp Business Platform API adaptoru.

WhatsApp Cloud API (Meta) uzerinden mesaj alip gonderir.
Webhook tabanli: Mesaj al -> Beyin'e gonder -> Cevabi WhatsApp'a gonder.

Bagimliliklar:
  - httpx (HTTP istemcisi)
  - cryptography (imza dogrulama icin, opsiyonel)

Yapilandirma (ortam degiskenleri):
  - WHATSAPP_API_KEY / WHATSAPP_ACCESS_TOKEN  — WhatsApp Graph API erisim tokeni
  - WHATSAPP_PHONE_NUMBER_ID                  — Isletme telefon numarasi ID'si
  - WHATSAPP_BUSINESS_ACCOUNT_ID              — Isletme hesabi ID'si (opsiyonel)
  - WHATSAPP_WEBHOOK_VERIFY_TOKEN             — Webhook dogrulama tokeni
  - WHATSAPP_API_VERSION                      — Graph API versiyonu (varsayilan: v22.0)

Webhook:
  POST /webhook/whatsapp  — Gelen mesajlari alir
  GET  /webhook/whatsapp  — Meta webhook dogrulamasi (hub.challenge)
"""

import asyncio
import hashlib
import hmac
import json
import logging
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# Proje kokunu sys.path'e ekle
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))

from reymen.gateway.config import Platform, PlatformConfig
from reymen.gateway.platforms.base import (
    BasePlatformAdapter,
    MessageEvent,
    MessageType,
    SendResult,
)
from reymen.gateway.session import SessionSource

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

# ---------------------------------------------------------------------------
# Sabitler
# ---------------------------------------------------------------------------

# Varsayilan Graph API versiyonu
_DEFAULT_API_VERSION = "v22.0"

# WhatsApp mesaj limiti (UTF-8 karakter)
WHATSAPP_MAX_MESSAGE_LENGTH = 4096

# Desteklenen medya tipleri (WhatsApp Cloud API)
WHATSAPP_IMAGE_TYPES = frozenset({
    "image/jpeg", "image/png", "image/webp",
})
WHATSAPP_AUDIO_TYPES = frozenset({
    "audio/ogg", "audio/mp3", "audio/mpeg", "audio/aac", "audio/mp4",
})
WHATSAPP_VIDEO_TYPES = frozenset({
    "video/mp4", "video/3gp",
})
WHATSAPP_DOCUMENT_TYPES = frozenset({
    "application/pdf",
    "text/plain", "text/csv",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
})

# Graph API temel URL'si
_GRAPH_API_BASE = "https://graph.facebook.com"

# ---------------------------------------------------------------------------
# Yardimci fonksiyonlar
# ---------------------------------------------------------------------------


def _env(key: str, default: str = "") -> str:
    """Ortam degiskenini okur, yoksa varsayilani dondurur."""
    return os.environ.get(key, default).strip()


def _env_required(key: str) -> str:
    """Zorunlu ortam degiskenini okur, yoksa hata firlatir."""
    value = _env(key)
    if not value:
        raise EnvironmentError(
            f"[WhatsApp] Eksik yapilandirma: {key} "
            f"ortam degiskeni ayarlanmamis."
        )
    return value


def _api_url(phone_number_id: str, action: str = "messages") -> str:
    """Graph API URL'sini olusturur."""
    version = _env("WHATSAPP_API_VERSION", _DEFAULT_API_VERSION)
    return (
        f"{_GRAPH_API_BASE}/{version}"
        f"/{phone_number_id}/{action}"
    )


def _media_url(media_id: str) -> str:
    """Medya indirme URL'sini olusturur."""
    version = _env("WHATSAPP_API_VERSION", _DEFAULT_API_VERSION)
    return f"{_GRAPH_API_BASE}/{version}/{media_id}"


def _headers(api_key: str) -> Dict[str, str]:
    """Graph API icin HTTP basliklari."""
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def _redact_phone(phone: str) -> str:
    """Telefon numarasini log icin maskele."""
    if not phone or len(phone) < 6:
        return "****"
    return phone[:3] + "****" + phone[-3:]


# ---------------------------------------------------------------------------
# WhatsApp mesaj modeli
# ---------------------------------------------------------------------------


@dataclass
class WhatsAppMessage:
    """WhatsApp'tan gelen normalize edilmis mesaj."""

    message_id: str
    from_number: str  # Gonderici telefon numarasi
    text: str = ""
    msg_type: str = "text"  # text, image, audio, video, document, location

    # Medya alanlari
    media_id: Optional[str] = None
    media_mime_type: Optional[str] = None
    media_filename: Optional[str] = None

    # Konum
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Zaman bilgisi
    timestamp: str = ""

    # Mesaj basligi (interactive list/reply mesajlari icin)
    context_message_id: Optional[str] = None
    button_reply: Optional[str] = None
    list_reply: Optional[str] = None

    # Orijinal webhook payload (debug icin)
    raw: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------------------------
# WhatsApp API Istemcisi
# ---------------------------------------------------------------------------


class WhatsAppClient:
    """WhatsApp Cloud API ile HTTP haberlesmesini yoneten istemci."""

    def __init__(
        self,
        api_key: str,
        phone_number_id: str,
        *,
        timeout: float = 30.0,
    ):
        """
        Args:
            api_key: WhatsApp Graph API erisim tokeni.
            phone_number_id: Isletme telefon numarasi ID'si.
            timeout: HTTP istek zamani asimi (saniye).
        """
        self._api_key = api_key
        self._phone_number_id = phone_number_id
        self._timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """HTTPX istemcisini tembel olarak olusturur."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self._timeout,
                headers=_headers(self._api_key),
            )
        return self._client

    async def close(self) -> None:
        """HTTPX istemcisini guvenli sekilde kapatir."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def send_text(
        self,
        to_number: str,
        text: str,
        *,
        preview_url: bool = False,
        context_message_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Metin mesaji gonderir.

        Args:
            to_number: Alici telefon numarasi.
            text: Mesaj metni.
            preview_url: URL onizlemesini ac/kapat.
            context_message_id: Yanitlanan mesajin ID'si (thread).

        Returns:
            Graph API yaniti.
        """
        payload: Dict[str, Any] = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "text",
            "text": {"preview_url": preview_url, "body": text},
        }
        if context_message_id:
            payload["context"] = {"message_id": context_message_id}
        return await self._post(payload)

    async def send_image(
        self,
        to_number: str,
        media_id_or_url: str,
        *,
        caption: Optional[str] = None,
        link: bool = False,
        context_message_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Resim mesaji gonderir.

        Args:
            to_number: Alici telefon numarasi.
            media_id_or_url: Medya ID'si veya URL.
            caption: Resim alt yazisi.
            link: True ise media_id_or_url URL olarak kullanilir.
            context_message_id: Yanitlanan mesajin ID'si.
        """
        media_field = {"link": media_id_or_url} if link else {"id": media_id_or_url}
        payload: Dict[str, Any] = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "image",
            "image": media_field,
        }
        if caption:
            payload["image"]["caption"] = caption
        if context_message_id:
            payload["context"] = {"message_id": context_message_id}
        return await self._post(payload)

    async def send_document(
        self,
        to_number: str,
        media_id_or_url: str,
        *,
        filename: Optional[str] = None,
        caption: Optional[str] = None,
        link: bool = False,
        context_message_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Belge mesaji gonderir.

        Args:
            to_number: Alici telefon numarasi.
            media_id_or_url: Medya ID'si veya URL.
            filename: Goruntulenecek dosya adi.
            caption: Belge alt yazisi.
            link: True ise media_id_or_url URL olarak kullanilir.
            context_message_id: Yanitlanan mesajin ID'si.
        """
        media_field = {"link": media_id_or_url} if link else {"id": media_id_or_url}
        if filename:
            media_field["filename"] = filename
        payload: Dict[str, Any] = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "document",
            "document": media_field,
        }
        if caption:
            payload["document"]["caption"] = caption
        if context_message_id:
            payload["context"] = {"message_id": context_message_id}
        return await self._post(payload)

    async def send_audio(
        self,
        to_number: str,
        media_id_or_url: str,
        *,
        link: bool = False,
        context_message_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Ses mesaji gonderir.

        Args:
            to_number: Alici telefon numarasi.
            media_id_or_url: Medya ID'si veya URL.
            link: True ise media_id_or_url URL olarak kullanilir.
            context_message_id: Yanitlanan mesajin ID'si.
        """
        media_field = {"link": media_id_or_url} if link else {"id": media_id_or_url}
        payload: Dict[str, Any] = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "audio",
            "audio": media_field,
        }
        if context_message_id:
            payload["context"] = {"message_id": context_message_id}
        return await self._post(payload)

    async def send_video(
        self,
        to_number: str,
        media_id_or_url: str,
        *,
        caption: Optional[str] = None,
        link: bool = False,
        context_message_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Video mesaji gonderir.

        Args:
            to_number: Alici telefon numarasi.
            media_id_or_url: Medya ID'si veya URL.
            caption: Video alt yazisi.
            link: True ise media_id_or_url URL olarak kullanilir.
            context_message_id: Yanitlanan mesajin ID'si.
        """
        media_field = {"link": media_id_or_url} if link else {"id": media_id_or_url}
        payload: Dict[str, Any] = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "video",
            "video": media_field,
        }
        if caption:
            payload["video"]["caption"] = caption
        if context_message_id:
            payload["context"] = {"message_id": context_message_id}
        return await self._post(payload)

    async def send_location(
        self,
        to_number: str,
        latitude: float,
        longitude: float,
        *,
        name: Optional[str] = None,
        address: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Konum mesaji gonderir.

        Args:
            to_number: Alici telefon numarasi.
            latitude: Enlem.
            longitude: Boylam.
            name: Konum adi (opsiyonel).
            address: Konum adresi (opsiyonel).
        """
        payload: Dict[str, Any] = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "location",
            "location": {
                "latitude": latitude,
                "longitude": longitude,
            },
        }
        if name:
            payload["location"]["name"] = name
        if address:
            payload["location"]["address"] = address
        return await self._post(payload)

    async def send_reaction(
        self,
        to_number: str,
        message_id: str,
        emoji: str,
    ) -> Dict[str, Any]:
        """
        Bir mesaja emoji tepkisi gonderir.

        Args:
            to_number: Alici telefon numarasi.
            message_id: Tepki verilecek mesajin ID'si.
            emoji: Tepki emojisi (ornek: "👍").
        """
        payload: Dict[str, Any] = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "reaction",
            "reaction": {"message_id": message_id, "emoji": emoji},
        }
        return await self._post(payload)

    async def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """
        Mesaji okundu olarak isaretler.

        Args:
            message_id: Okundu bilgisi gonderilecek mesaj ID'si.
        """
        payload: Dict[str, Any] = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }
        return await self._post(payload)

    async def upload_media(
        self,
        file_path: str,
        mime_type: str,
    ) -> Optional[str]:
        """
        Medya dosyasini WhatsApp sunucusuna yukler.

        Args:
            file_path: Yuklenecek dosyanin yolu.
            mime_type: Dosyanin MIME tipi.

        Returns:
            Medya ID'si veya basarisizlik durumunda None.
        """
        try:
            client = await self._get_client()
            url = _api_url(self._phone_number_id, "media")
            with open(file_path, "rb") as f:
                files = {
                    "file": (os.path.basename(file_path), f, mime_type),
                    "messaging_product": (None, "whatsapp"),
                }
                resp = await client.post(url, files=files)
                resp.raise_for_status()
                data = resp.json()
                return data.get("id")
        except Exception as exc:
            logger.error(
                "[WhatsApp] Medya yukleme hatasi (%s): %s",
                file_path, exc,
            )
            return None

    async def download_media(self, media_id: str) -> Optional[bytes]:
        """
        Medyayi WhatsApp sunucusundan indirir.

        Args:
            media_id: Medya ID'si.

        Returns:
            Ham medya verisi veya None.
        """
        try:
            client = await self._get_client()

            # Once medya bilgisini al (URL icin)
            url = _media_url(media_id)
            info_resp = await client.get(url)
            info_resp.raise_for_status()
            media_info = info_resp.json()
            download_url = media_info.get("url")
            mime_type = media_info.get("mime_type", "")

            if not download_url:
                logger.warning(
                    "[WhatsApp] Medya URL'si bulunamadi: %s", media_id
                )
                return None

            # Medyayi indir
            dl_resp = await client.get(download_url)
            dl_resp.raise_for_status()
            return dl_resp.content
        except Exception as exc:
            logger.error(
                "[WhatsApp] Medya indirme hatasi (%s): %s", media_id, exc,
            )
            return None

    async def get_business_profile(self) -> Optional[Dict[str, Any]]:
        """Isletme profili bilgilerini getirir."""
        try:
            client = await self._get_client()
            version = _env("WHATSAPP_API_VERSION", _DEFAULT_API_VERSION)
            url = (
                f"{_GRAPH_API_BASE}/{version}"
                f"/{self._phone_number_id}"
                f"?fields=verified_name,display_phone_number"
            )
            resp = await client.get(url, headers=_headers(self._api_key))
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            logger.error("[WhatsApp] Profil bilgisi alinamadi: %s", exc)
            return None

    async def _post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Graph API'ye POST istegi gonderir."""
        client = await self._get_client()
        url = _api_url(self._phone_number_id, "messages")
        resp = await client.post(url, json=payload)
        try:
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as exc:
            error_body = ""
            try:
                error_body = resp.text
            except Exception:
                pass
            logger.error(
                "[WhatsApp] API hatasi (%s): %s — %s",
                resp.status_code,
                exc,
                error_body[:500] if error_body else "",
            )
            raise
        except Exception as exc:
            logger.error("[WhatsApp] Istek hatasi: %s", exc)
            raise


# ---------------------------------------------------------------------------
# Webhook payload ayristirici
# ---------------------------------------------------------------------------


class WhatsAppWebhookParser:
    """Meta'dan gelen webhook payload'ini :class:`WhatsAppMessage`'e cevirir."""

    @staticmethod
    def parse(payload: Dict[str, Any]) -> List[WhatsAppMessage]:
        """
        Webhook payload'ini ayristirip WhatsAppMessage listesi dondurur.

        Args:
            payload: Ham webhook JSON dict.

        Returns:
            WhatsAppMessage nesnelerinin listesi.
        """
        messages: List[WhatsAppMessage] = []

        try:
            entries = payload.get("entry", [])
        except Exception:
            logger.warning("[WhatsApp] Webhook payload gecersiz yapi")
            return messages

        for entry in entries:
            try:
                changes = entry.get("changes", [])
            except Exception:
                continue

            for change in changes:
                try:
                    value = change.get("value", {})
                except Exception:
                    continue

                # Mesaj var mi?
                raw_messages = value.get("messages", [])
                if not raw_messages:
                    continue

                # Metadata (phone_number_id)
                metadata = value.get("metadata", {})
                display_phone = metadata.get("display_phone_number", "")
                phone_number_id = metadata.get("phone_number_id", "")

                for raw_msg in raw_messages:
                    try:
                        msg = WhatsAppWebhookParser._parse_single(
                            raw_msg, display_phone, phone_number_id,
                        )
                        if msg:
                            messages.append(msg)
                    except Exception as exc:
                        logger.warning(
                            "[WhatsApp] Mesaj ayristirma hatasi: %s — %s",
                            exc,
                            str(raw_msg)[:200],
                        )

        return messages

    @staticmethod
    def _parse_single(
        raw: Dict[str, Any],
        display_phone: str,
        phone_number_id: str,
    ) -> Optional[WhatsAppMessage]:
        """Tek bir mesaji ayristirir."""
        msg_id = raw.get("id", "")
        if not msg_id:
            return None

        from_number = raw.get("from", "")
        timestamp = raw.get("timestamp", "")

        # Context bilgisi (yanitlanan mesaj)
        context = raw.get("context", {}) or {}
        context_message_id = context.get("id") if isinstance(context, dict) else None

        # Mesaj tipini belirle
        msg_type = raw.get("type", "unknown")

        # Text
        text = ""
        if msg_type == "text":
            text_body = raw.get("text", {}) or {}
            text = text_body.get("body", "") if isinstance(text_body, dict) else ""

        # Interactive (button/list reply)
        button_reply = None
        list_reply = None
        if msg_type == "interactive":
            interactive = raw.get("interactive", {}) or {}
            if isinstance(interactive, dict):
                btn = interactive.get("button_reply", {}) or {}
                if isinstance(btn, dict):
                    button_reply = btn.get("id") or btn.get("title")
                lst = interactive.get("list_reply", {}) or {}
                if isinstance(lst, dict):
                    list_reply = lst.get("id") or lst.get("title")

        # Button reply'i text olarak kullan
        if button_reply:
            text = button_reply if isinstance(button_reply, str) else str(button_reply)
            msg_type = "text"

        if list_reply:
            text = list_reply if isinstance(list_reply, str) else str(list_reply)
            msg_type = "text"

        # Medya
        media_id = None
        media_mime = None
        media_filename = None

        if msg_type == "image":
            img = raw.get("image", {}) or {}
            if isinstance(img, dict):
                media_id = img.get("id")
                media_mime = img.get("mime_type")
                caption = img.get("caption", "")
                text = caption or ""

        elif msg_type == "audio":
            aud = raw.get("audio", {}) or {}
            if isinstance(aud, dict):
                media_id = aud.get("id")
                media_mime = aud.get("mime_type")

        elif msg_type == "video":
            vid = raw.get("video", {}) or {}
            if isinstance(vid, dict):
                media_id = vid.get("id")
                media_mime = vid.get("mime_type")
                caption = vid.get("caption", "")
                text = caption or ""

        elif msg_type == "document":
            doc = raw.get("document", {}) or {}
            if isinstance(doc, dict):
                media_id = doc.get("id")
                media_mime = doc.get("mime_type")
                media_filename = doc.get("filename", "")
                caption = doc.get("caption", "")
                text = caption or ""

        elif msg_type == "location":
            loc = raw.get("location", {}) or {}
            if isinstance(loc, dict):
                latitude = loc.get("latitude")
                longitude = loc.get("longitude")
                if latitude is not None and longitude is not None:
                    text = f"Konum: {latitude}, {longitude}"
                    return WhatsAppMessage(
                        message_id=msg_id,
                        from_number=from_number,
                        text=text,
                        msg_type="location",
                        latitude=float(latitude),
                        longitude=float(longitude),
                        timestamp=timestamp,
                        context_message_id=context_message_id,
                        raw=raw,
                    )

        # Bilinmeyen mesaj türü
        if msg_type == "unknown":
            logger.debug("[WhatsApp] Atlanan bilinmeyen mesaj turu: %s", raw.get("type"))
            return None

        return WhatsAppMessage(
            message_id=msg_id,
            from_number=from_number,
            text=text,
            msg_type=msg_type,
            media_id=media_id,
            media_mime_type=media_mime,
            media_filename=media_filename,
            timestamp=timestamp,
            context_message_id=context_message_id,
            button_reply=button_reply,
            list_reply=list_reply,
            raw=raw,
        )


# ---------------------------------------------------------------------------
# Webhook imza dogrulama
# ---------------------------------------------------------------------------


def verify_webhook_signature(
    payload_body: bytes,
    signature_header: str,
    app_secret: str,
) -> bool:
    """
    Meta webhook imzasini dogrular.

    Meta, her webhook istegine ``X-Hub-Signature-256`` basliginda
    HMAC-SHA256 imzasi ekler. Bu fonksiyon imzayi dogrular.

    Args:
        payload_body: Ham istek govdesi (bytes).
        signature_header: ``X-Hub-Signature-256`` baslik degeri.
        app_secret: WhatsApp uygulama secret'i.

    Returns:
        Imza gecerliyse True.
    """
    if not signature_header:
        return False

    # "sha256=..." formatini ayristir
    expected_prefix = "sha256="
    if not signature_header.startswith(expected_prefix):
        return False
    received_sig = signature_header[len(expected_prefix):]

    try:
        expected_sig = hmac.new(
            app_secret.encode("utf-8"),
            payload_body,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected_sig, received_sig)
    except Exception as exc:
        logger.warning("[WhatsApp] Imza dogrulama hatasi: %s", exc)
        return False


def verify_webhook_challenge(
    query_params: Dict[str, str],
    verify_token: str,
) -> Optional[str]:
    """
    Meta webhook dogrulama istegini (GET) yanitlar.

    Meta, webhook'u kaydederken bir dogrulama istegi gonderir:
    ``GET /webhook/whatsapp?hub.mode=subscribe&hub.verify_token=...&hub.challenge=...``

    Args:
        query_params: Istek query parametreleri sozlugu.
        verify_token: Beklenen dogrulama tokeni.

    Returns:
        ``hub.challenge`` degeri (doganayi saglarsa), yoksa None.
    """
    mode = query_params.get("hub.mode", "")
    token = query_params.get("hub.verify_token", "")
    challenge = query_params.get("hub.challenge")

    if mode == "subscribe" and token == verify_token and challenge:
        return challenge
    return None


# ---------------------------------------------------------------------------
# Medya indirme ve orteleme
# ---------------------------------------------------------------------------


async def _download_and_cache_media(
    client: WhatsAppClient,
    media_id: str,
    mime_type: Optional[str],
) -> Optional[str]:
    """Medyayi indirir ve gecici dosyaya kaydeder. Yerel yolu dondurur."""
    if not media_id:
        return None

    try:
        data = await client.download_media(media_id)
        if data is None:
            return None

        # Uzantiyi MIME tipinden cikar
        ext = _mime_to_ext(mime_type or "application/octet-stream")

        # Gecici dosyaya yaz
        suffix = f".{ext}" if ext else ""
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=suffix, prefix="whatsapp_"
        ) as tmp:
            tmp.write(data)
            return tmp.name
    except Exception as exc:
        logger.error("[WhatsApp] Medya orteleme hatasi (%s): %s", media_id, exc)
        return None


def _mime_to_ext(mime_type: str) -> str:
    """MIME tipinden dosya uzantisi tahmin eder."""
    mime_to_ext = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
        "audio/ogg": "ogg",
        "audio/mp3": "mp3",
        "audio/mpeg": "mp3",
        "audio/aac": "aac",
        "audio/mp4": "m4a",
        "video/mp4": "mp4",
        "video/3gp": "3gp",
        "application/pdf": "pdf",
        "text/plain": "txt",
        "text/csv": "csv",
    }
    return mime_to_ext.get(mime_type.lower(), "")


# ---------------------------------------------------------------------------
# WhatsApp Gateway Adaptoru
# ---------------------------------------------------------------------------


class WhatsAppAdapter(BasePlatformAdapter):
    """
    WhatsApp Business Platform API adaptoru.

    Webhook tabanli calisir:
    - ``POST /webhook/whatsapp`` ile mesaj alir
    - Mesaji :class:`~reymen.gateway.platforms.base.MessageEvent`'e cevirir
    - Beyin'e (message handler) gonderir
    - Yaniti WhatsApp Cloud API uzerinden gonderir

    Kullanim (config.yaml)::

        platforms:
          whatsapp:
            enabled: true
            extra:
              phone_number_id: "123456789"
              access_token: "EAAx..."
              verify_token: "my_verify_token"
              app_secret: "my_app_secret"

    Veya ortam degiskenleri:
    - ``WHATSAPP_PHONE_NUMBER_ID``
    - ``WHATSAPP_ACCESS_TOKEN`` veya ``WHATSAPP_API_KEY``
    - ``WHATSAPP_WEBHOOK_VERIFY_TOKEN``
    - ``WHATSAPP_APP_SECRET`` (imza dogrulama icin, opsiyonel)
    """

    MAX_MESSAGE_LENGTH = WHATSAPP_MAX_MESSAGE_LENGTH
    supports_code_blocks = False  # WhatsApp sadece duz metin

    def __init__(self, config: PlatformConfig):
        """
        Args:
            config: Platform yapilandirmasi.
        """
        super().__init__(config, Platform.WHATSAPP)

        # API anahtari
        self._api_key = (
            config.api_key
            or config.extra.get("access_token")
            or config.extra.get("api_key")
            or _env("WHATSAPP_ACCESS_TOKEN")
            or _env("WHATSAPP_API_KEY")
            or ""
        )

        # Telefon numarasi ID'si
        self._phone_number_id = (
            config.extra.get("phone_number_id")
            or _env("WHATSAPP_PHONE_NUMBER_ID")
            or ""
        )

        # Webhook dogrulama tokeni
        self._verify_token = (
            config.extra.get("verify_token")
            or _env("WHATSAPP_WEBHOOK_VERIFY_TOKEN")
            or "reymen_whatsapp_verify"
        )

        # Uygulama secret (imza dogrulama icin)
        self._app_secret = (
            config.extra.get("app_secret")
            or _env("WHATSAPP_APP_SECRET")
            or ""
        )

        # HTTPX istemcisi
        self._client: Optional[WhatsAppClient] = None

        # Durum
        self._connected = False

    @property
    def enforces_own_access_policy(self) -> bool:
        """WhatsApp kendi erisim politikasini uygular."""
        return True

    async def connect(self) -> bool:
        """
        WhatsApp API baglantisini baslatir.

        Gerekli yapilandirma kontrol edilir ve bir test istegi
        (business profile sorgulama) ile baglanti dogrulanir.

        Returns:
            Baglanti basariliysa True.
        """
        try:
            # Gerekli alanlari kontrol et
            if not HTTPX_AVAILABLE:
                logger.error(
                    "[WhatsApp] httpx kutuphanesi bulunamadi. "
                    "Kurulum: pip install httpx"
                )
                self._set_fatal_error(
                    "missing_dependency",
                    "httpx kutuphanesi bulunamadi",
                    retryable=False,
                )
                return False

            if not self._api_key:
                logger.error(
                    "[WhatsApp] API anahtari bulunamadi. "
                    "WHATSAPP_API_KEY veya WHATSAPP_ACCESS_TOKEN ayarlayin."
                )
                self._set_fatal_error(
                    "missing_api_key",
                    "WhatsApp API anahtari bulunamadi",
                    retryable=False,
                )
                return False

            if not self._phone_number_id:
                logger.error(
                    "[WhatsApp] Telefon numarasi ID'si bulunamadi. "
                    "WHATSAPP_PHONE_NUMBER_ID ayarlayin."
                )
                self._set_fatal_error(
                    "missing_phone_number_id",
                    "WhatsApp telefon numarasi ID'si bulunamadi",
                    retryable=False,
                )
                return False

            # WhatsApp API istemcisini olustur
            self._client = WhatsAppClient(
                api_key=self._api_key,
                phone_number_id=self._phone_number_id,
            )

            # Baglantiyi dogrula
            profile = await self._client.get_business_profile()
            if profile is None:
                logger.error(
                    "[WhatsApp] Baglanti dogrulamasi basarisiz. "
                    "API anahtari veya telefon numarasi ID'si hatali olabilir."
                )
                self._set_fatal_error(
                    "auth_failed",
                    "WhatsApp API baglantisi dogrulanamadi",
                    retryable=True,
                )
                return False

            verified_name = profile.get("verified_name", "Bilinmiyor")
            display_phone = profile.get("display_phone_number", "Bilinmiyor")
            logger.info(
                "[WhatsApp] Baglanti basarili — %s (%s)",
                verified_name,
                display_phone,
            )

            self._connected = True
            self._mark_connected()
            return True

        except Exception as exc:
            logger.error("[WhatsApp] Baglanti hatasi: %s", exc, exc_info=True)
            self._set_fatal_error(
                "connection_failed",
                f"WhatsApp baglantisi basarisiz: {exc}",
                retryable=True,
            )
            return False

    async def disconnect(self) -> None:
        """WhatsApp API baglantisini kapatir."""
        self._connected = False
        if self._client:
            try:
                await self._client.close()
            except Exception as exc:
                logger.debug("[WhatsApp] Kapatma hatasi: %s", exc)
            self._client = None
        self._mark_disconnected()
        logger.info("[WhatsApp] Baglanti kapatildi")

    async def send(
        self,
        chat_id: str,
        content: str,
        reply_to: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SendResult:
        """
        WhatsApp'a metin mesaji gonderir.

        Args:
            chat_id: Alici telefon numarasi (uluslararasi format, or: ``905551234567``).
            content: Mesaj metni.
            reply_to: Yanitlanacak mesaj ID'si (opsiyonel).
            metadata: Ek opsiyonlar (``preview_url``, vb.).

        Returns:
            Gonderim sonucu.
        """
        if not self._connected or not self._client:
            return SendResult(
                success=False,
                error="WhatsApp baglisi degil",
                retryable=True,
            )

        try:
            preview_url = bool(
                (metadata or {}).get("preview_url", False)
            )

            result = await self._client.send_text(
                to_number=chat_id,
                text=content,
                preview_url=preview_url,
                context_message_id=reply_to,
            )

            messages = result.get("messages", [{}])
            message_id = messages[0].get("id") if messages else None

            logger.info(
                "[WhatsApp] Mesaj gonderildi -> %s (id: %s)",
                _redact_phone(chat_id),
                message_id,
            )

            return SendResult(
                success=True,
                message_id=message_id,
            )

        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code if exc.response else 0
            is_retryable = status in (429, 500, 502, 503, 504)
            logger.error(
                "[WhatsApp] Gonderim hatasi (HTTP %s): %s",
                status,
                exc,
            )
            return SendResult(
                success=False,
                error=f"HTTP {status}: {exc}",
                retryable=is_retryable,
            )

        except Exception as exc:
            logger.error(
                "[WhatsApp] Gonderim hatasi (%s): %s",
                _redact_phone(chat_id),
                exc,
            )
            return SendResult(
                success=False,
                error=str(exc),
                retryable=True,
            )

    async def send_image(
        self,
        chat_id: str,
        image_url: str,
        caption: Optional[str] = None,
        reply_to: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SendResult:
        """
        WhatsApp'a resim gonderir.

        Args:
            chat_id: Alici telefon numarasi.
            image_url: Resim URL'si veya yerel dosya yolu.
            caption: Resim alt yazisi.
            reply_to: Yanitlanacak mesaj ID'si.
            metadata: Ek opsiyonlar.

        Returns:
            Gonderim sonucu.
        """
        if not self._connected or not self._client:
            return SendResult(
                success=False,
                error="WhatsApp baglisi degil",
                retryable=True,
            )

        try:
            # URL'den gonder
            if image_url.startswith(("http://", "https://")):
                result = await self._client.send_image(
                    to_number=chat_id,
                    media_id_or_url=image_url,
                    caption=caption,
                    link=True,
                    context_message_id=reply_to,
                )
            else:
                # Yerel dosyayi yukle
                mime_type = _guess_mime_from_path(image_url)
                media_id = await self._client.upload_media(image_url, mime_type)
                if not media_id:
                    return SendResult(
                        success=False,
                        error="Medya yuklenemedi",
                        retryable=False,
                    )
                result = await self._client.send_image(
                    to_number=chat_id,
                    media_id_or_url=media_id,
                    caption=caption,
                    context_message_id=reply_to,
                )

            messages = result.get("messages", [{}])
            message_id = messages[0].get("id") if messages else None

            return SendResult(success=True, message_id=message_id)

        except Exception as exc:
            logger.error("[WhatsApp] Resim gonderim hatasi: %s", exc)
            return SendResult(
                success=False,
                error=str(exc),
                retryable=True,
            )

    async def send_typing(self, chat_id: str, metadata=None) -> None:
        """
        WhatsApp'ta yaziyor gostergesini gonderir.

        Not: WhatsApp Cloud API dogrudan ``typing`` gostergesi
        gondermeyi desteklemez. Bunun yerine ``mark_as_read``
        kullanilabilir.

        Args:
            chat_id: Alici telefon numarasi.
            metadata: Kullanilmiyor.
        """
        # WhatsApp'ta native typing indicator yok.
        # Bazi alternatif cozumler:
        # - Mesaji okundu olarak isaretle
        # - Bos mesaj gonder (oneri LMEZ)
        pass

    async def handle_webhook(
        self,
        payload: Dict[str, Any],
    ) -> Optional[str]:
        """
        Webhook'tan gelen mesaji isler.

        Bu metot dogrudan bir HTTP endpoint tarafindan cagrilir.
        Gelen mesaji ayristirir, MessageEvent'e cevirir ve
        kayitli message handler'a iletir.

        Args:
            payload: Webhook JSON payload'i.

        Returns:
            Basit HTTP yaniti metni ("OK" veya benzeri).
        """
        if not self._message_handler:
            logger.warning("[WhatsApp] Mesaj handler'i kayitli degil")
            return "ERROR: No handler"

        try:
            messages = WhatsAppWebhookParser.parse(payload)
        except Exception as exc:
            logger.error("[WhatsApp] Webhook ayristirma hatasi: %s", exc)
            return "ERROR: Parse failed"

        if not messages:
            logger.debug("[WhatsApp] Islenecek mesaj yok (status guncellemesi olabilir)")
            return "OK"

        for wa_msg in messages:
            try:
                await self._process_whatsapp_message(wa_msg)
            except Exception as exc:
                logger.error(
                    "[WhatsApp] Mesaj isleme hatasi (%s): %s",
                    _redact_phone(wa_msg.from_number),
                    exc,
                    exc_info=True,
                )

        return "OK"

    async def _process_whatsapp_message(self, wa_msg: WhatsAppMessage) -> None:
        """Tek bir WhatsApp mesajini MessageEvent'e cevirip handler'a iletir."""
        # Mesaj tipini belirle
        msg_type = self._resolve_message_type(wa_msg)

        # Medya dosyalarini indir (varsa)
        media_urls: List[str] = []
        media_types: List[str] = []

        if wa_msg.media_id and self._client:
            local_path = await _download_and_cache_media(
                self._client,
                wa_msg.media_id,
                wa_msg.media_mime_type,
            )
            if local_path:
                media_urls.append(local_path)
                media_types.append(wa_msg.media_mime_type or "application/octet-stream")

        # Konum mesaji
        if wa_msg.msg_type == "location" and wa_msg.latitude is not None:
            lat_lng_text = (
                f"Kullanici konum gonderdi:\n"
                f"Enlem: {wa_msg.latitude}\n"
                f"Boylam: {wa_msg.longitude}"
            )
            wa_msg.text = lat_lng_text

        # SessionSource olustur
        source = SessionSource(
            platform=Platform.WHATSAPP,
            chat_id=wa_msg.from_number,
            user_id=wa_msg.from_number,
            chat_type="dm",  # WhatsApp birebir mesaj
        )

        event = MessageEvent(
            text=wa_msg.text or "",
            message_type=msg_type,
            source=source,
            message_id=wa_msg.message_id,
            reply_to_message_id=wa_msg.context_message_id,
            media_urls=media_urls,
            media_types=media_types,
            raw_message=wa_msg.raw,
            timestamp=datetime.fromtimestamp(
                int(wa_msg.timestamp) if wa_msg.timestamp.isdigit() else 0,
                tz=timezone.utc,
            ) if wa_msg.timestamp else datetime.now(timezone.utc),
        )

        logger.info(
            "[WhatsApp] Mesaj alindi: %s -> \"%s\"%s",
            _redact_phone(wa_msg.from_number),
            (wa_msg.text or "")[:80],
            f" [+{len(media_urls)} medya]" if media_urls else "",
        )

        try:
            response = await self._message_handler(event)
            if response:
                await self.send(
                    chat_id=wa_msg.from_number,
                    content=response,
                    reply_to=wa_msg.message_id,
                )
        except Exception as exc:
            logger.error(
                "[WhatsApp] Beyin isleme hatasi: %s",
                exc,
                exc_info=True,
            )

    def _resolve_message_type(self, wa_msg: WhatsAppMessage) -> MessageType:
        """WhatsApp mesaj tipini :class:`MessageType` degere cevirir."""
        type_map = {
            "text": MessageType.TEXT,
            "image": MessageType.PHOTO,
            "audio": MessageType.AUDIO,
            "voice": MessageType.AUDIO,
            "video": MessageType.VIDEO,
            "document": MessageType.DOCUMENT,
            "location": MessageType.LOCATION,
        }
        return type_map.get(wa_msg.msg_type, MessageType.TEXT)

    def get_webhook_routes(self) -> List[Dict[str, Any]]:
        """
        Webhook icin HTTP route bilgilerini dondurur.

        Gateway'in HTTP sunucusu bu route'lari kaydederek
        WhatsApp webhook isteklerini bu adaptore yonlendirir.

        Returns:
            Route tanimlari sozlugu listesi.
        """
        return [
            {
                "path": "/webhook/whatsapp",
                "methods": ["POST", "GET"],
                "handler": self._webhook_handler,
            },
        ]

    async def _webhook_handler(self, request: Any) -> Any:
        """
        Webhook HTTP isteklerini isler.

        - GET: Meta webhook dogrulamasi (hub.challenge)
        - POST: Gelen mesajlar
        """
        try:
            method = request.method.upper() if hasattr(request, "method") else "POST"
        except Exception:
            method = "POST"

        if method == "GET":
            return await self._handle_verify(request)

        return await self._handle_webhook_post(request)

    async def _handle_verify(self, request: Any) -> Any:
        """Webhook dogrulama GET istegini isler."""
        try:
            query = {}
            if hasattr(request, "query_params"):
                query = dict(request.query_params)
            elif hasattr(request, "args"):
                query = dict(request.args)
        except Exception:
            query = {}

        challenge = verify_webhook_challenge(query, self._verify_token)
        if challenge:
            logger.info("[WhatsApp] Webhook dogrulandi")
            # HTTP yaniti olarak challenge degerini dondur
            return _http_response(body=challenge, status=200)

        logger.warning("[WhatsApp] Webhook dogrulama basarisiz")
        return _http_response(body="Verification failed", status=403)

    async def _handle_webhook_post(self, request: Any) -> Any:
        """Webhook POST istegini isler."""
        try:
            if hasattr(request, "body"):
                body = await request.body()
            elif hasattr(request, "data"):
                body = request.data
            else:
                body = b""
        except Exception:
            body = b""

        # Imza dogrulama (opsiyonel)
        if self._app_secret:
            sig_header = ""
            if hasattr(request, "headers"):
                sig_header = request.headers.get("X-Hub-Signature-256", "")
            elif hasattr(request, "headers") and callable(getattr(request, "headers", None)):
                sig_header = request.headers.get("X-Hub-Signature-256", "")

            if sig_header and not verify_webhook_signature(
                body, sig_header, self._app_secret,
            ):
                logger.warning("[WhatsApp] Webhook imza dogrulama basarisiz")
                return _http_response(body="Invalid signature", status=403)

        try:
            payload = json.loads(body) if body else {}
        except json.JSONDecodeError as exc:
            logger.error("[WhatsApp] Webhook JSON ayristirma hatasi: %s", exc)
            return _http_response(body="Invalid JSON", status=400)

        try:
            await self.handle_webhook(payload)
        except Exception as exc:
            logger.error(
                "[WhatsApp] Webhook isleme hatasi: %s",
                exc,
                exc_info=True,
            )

        return _http_response(body="OK", status=200)

    def __repr__(self) -> str:
        return (
            f"<WhatsAppAdapter phone={_redact_phone(self._phone_number_id)} "
            f"connected={self._connected}>"
        )


# ---------------------------------------------------------------------------
# HTTP yaniti yardimcisi
# ---------------------------------------------------------------------------


def _http_response(*, body: str, status: int = 200) -> Dict[str, Any]:
    """
    Basit bir HTTP yaniti dict'i olusturur.

    Gateway'in HTTP sunucusu bu formati anlamalidir.
    """
    return {
        "status_code": status,
        "body": body,
        "content_type": "text/plain",
    }


# ---------------------------------------------------------------------------
# MIME tespit yardimcisi
# ---------------------------------------------------------------------------


def _guess_mime_from_path(file_path: str) -> str:
    """Dosya yolundan MIME tipi tahmin eder."""
    ext = os.path.splitext(file_path)[1].lower()
    ext_to_mime = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
        ".mp3": "audio/mpeg",
        ".m4a": "audio/mp4",
        ".ogg": "audio/ogg",
        ".wav": "audio/wav",
        ".mp4": "video/mp4",
        ".pdf": "application/pdf",
        ".txt": "text/plain",
        ".csv": "text/csv",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    return ext_to_mime.get(ext, "application/octet-stream")
