"""
ReYMeN Gateway — Email platform adapter.

SMTP (outgoing) ve IMAP (incoming) uzerinden email mesajlasmasi saglar.
Python built-in kutuphaneleri kullanir (smtplib, imaplib, email).

Yapilandirma (ortam degiskenleri):
  EMAIL_SMTP_HOST     — SMTP sunucu adresi (ornek: smtp.gmail.com)
  EMAIL_SMTP_PORT     — SMTP portu (ornek: 587)
  EMAIL_IMAP_HOST     — IMAP sunucu adresi (ornek: imap.gmail.com)
  EMAIL_IMAP_PORT     — IMAP portu (ornek: 993)
  EMAIL_ADDRESS       — E-posta adresi (ornek: user@gmail.com)
  EMAIL_PASSWORD      — E-posta sifresi / uygulama sifresi
"""

import asyncio
import email as email_lib
import imaplib
import logging
import os
import smtplib
import sys
from datetime import datetime, timezone
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, parsedate_to_datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

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

# smtplib, imaplib, email Python built-in — ek bagimlilik gerekmez.

EMAIL_AVAILABLE = True


def check_email_requirements() -> bool:
    """Check if required env vars are set."""
    required = ["EMAIL_SMTP_HOST", "EMAIL_ADDRESS", "EMAIL_PASSWORD"]
    for key in required:
        if not os.environ.get(key, "").strip():
            logger.warning("[Email] Eksik yapilandirma: %s", key)
            return False
    return True


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


def _env_int(key: str, default: int) -> int:
    raw = _env(key)
    if not raw:
        return default
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


def _decode_email_header(header_value: str) -> str:
    """Decode an email header (e.g. Subject, From) to plain text."""
    if not header_value:
        return ""
    parts = decode_header(header_value)
    decoded_parts: List[str] = []
    for part, charset in parts:
        if isinstance(part, bytes):
            try:
                charset = charset or "utf-8"
                decoded_parts.append(part.decode(charset, errors="replace"))
            except (LookupError, UnicodeDecodeError):
                decoded_parts.append(part.decode("utf-8", errors="replace"))
        else:
            decoded_parts.append(str(part))
    return " ".join(decoded_parts)


def _extract_text_from_message(msg: Any) -> str:
    """Extract plain text body from an email message."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    try:
                        return payload.decode(charset, errors="replace")
                    except (LookupError, UnicodeDecodeError):
                        return payload.decode("utf-8", errors="replace")
            elif content_type == "text/html":
                # Fallback: HTML icerigini duz metne cevir
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    try:
                        return payload.decode(charset, errors="replace")
                    except (LookupError, UnicodeDecodeError):
                        return payload.decode("utf-8", errors="replace")
        return ""
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            try:
                return payload.decode(charset, errors="replace")
            except (LookupError, UnicodeDecodeError):
                return payload.decode("utf-8", errors="replace")
        return ""


# ---------------------------------------------------------------------------
# Email Adapter
# ---------------------------------------------------------------------------


class EmailAdapter(BasePlatformAdapter):
    """
    Email platform adapter.

    SMTP ile mesaj gonderir, IMAP ile gelen mesajlari okur.
    Her bir e-posta konusmasi bir "chat" olarak ele alinir;
    chat_id = gonderici/adres e-posta adresidir.
    """

    MAX_MESSAGE_LENGTH = 100000  # Email genelde cok buyuk mesajlara izin verir
    supports_code_blocks = True  # HTML e-posta ile code block render edilebilir

    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform.EMAIL)

        # Ortam degiskenlerinden yapilandirma
        self._smtp_host: str = _env("EMAIL_SMTP_HOST", "")
        self._smtp_port: int = _env_int("EMAIL_SMTP_PORT", 587)
        self._imap_host: str = _env("EMAIL_IMAP_HOST", "")
        self._imap_port: int = _env_int("EMAIL_IMAP_PORT", 993)
        self._email_address: str = _env("EMAIL_ADDRESS", "")
        self._email_password: str = _env("EMAIL_PASSWORD", "")

        # SMTP/IMAP baglantilari
        self._smtp: Optional[smtplib.SMTP] = None
        self._imap: Optional[imaplib.IMAP4_SSL] = None

        # IMAP polling
        self._poll_task: Optional[asyncio.Task] = None
        self._poll_interval: float = 30.0  # saniye

        # Mesaj tekrar korumasi (IMAP UID bazli)
        self._seen_uids: set = set()
        self._dedup = MessageDeduplicator()

        # Durum
        self._connected = False

    # ------------------------------------------------------------------
    # Property overrides
    # ------------------------------------------------------------------

    @property
    def enforces_own_access_policy(self) -> bool:
        """Email kendi erisim politikasini uygulamaz, gateway yonetsin."""
        return False

    @property
    def is_connected(self) -> bool:
        return self._connected

    # ------------------------------------------------------------------
    # SMTP helpers
    # ------------------------------------------------------------------

    async def _connect_smtp(self) -> bool:
        """SMTP sunucusuna baglan ve giris yap."""
        try:
            if not self._smtp_host or not self._email_address or not self._email_password:
                logger.error("[Email] SMTP yapilandirmasi eksik")
                return False

            smtp = smtplib.SMTP(self._smtp_host, self._smtp_port, timeout=30)
            smtp.ehlo()
            if smtp.has_extn("STARTTLS"):
                smtp.starttls()
                smtp.ehlo()
            smtp.login(self._email_address, self._email_password)
            self._smtp = smtp
            logger.info(
                "[Email] SMTP baglantisi basarili: %s:%d",
                self._smtp_host,
                self._smtp_port,
            )
            return True
        except (smtplib.SMTPException, ConnectionError, OSError) as e:
            logger.error("[Email] SMTP baglanti hatasi: %s", e)
            return False

    async def _disconnect_smtp(self) -> None:
        """SMTP baglantisini kapat."""
        if self._smtp is not None:
            try:
                self._smtp.quit()
            except Exception:
                try:
                    self._smtp.close()
                except Exception:
                    pass
            self._smtp = None

    # ------------------------------------------------------------------
    # IMAP helpers
    # ------------------------------------------------------------------

    async def _connect_imap(self) -> bool:
        """IMAP sunucusuna baglan ve giris yap."""
        try:
            if not self._imap_host or not self._email_address or not self._email_password:
                logger.error("[Email] IMAP yapilandirmasi eksik")
                return False

            imap = imaplib.IMAP4_SSL(self._imap_host, self._imap_port, timeout=30)
            imap.login(self._email_address, self._email_password)
            self._imap = imap
            logger.info(
                "[Email] IMAP baglantisi basarili: %s:%d",
                self._imap_host,
                self._imap_port,
            )
            return True
        except (imaplib.IMAP4.error, ConnectionError, OSError) as e:
            logger.error("[Email] IMAP baglanti hatasi: %s", e)
            return False

    async def _disconnect_imap(self) -> None:
        """IMAP baglantisini kapat."""
        if self._imap is not None:
            try:
                self._imap.logout()
            except Exception:
                pass
            self._imap = None

    async def _fetch_new_messages(self) -> List[MessageEvent]:
        """IMAP uzerinden yeni mesajlari getir."""
        if self._imap is None:
            return []

        events: List[MessageEvent] = []

        try:
            self._imap.select("INBOX", readonly=True)

            # Okunmamis mesajlari ara
            status, messages = self._imap.search(None, "UNSEEN")
            if status != "OK" or not messages[0]:
                return events

            uids = messages[0].split()
            for uid_bytes in uids:
                uid_str = uid_bytes.decode() if isinstance(uid_bytes, bytes) else str(uid_bytes)
                if uid_str in self._seen_uids:
                    continue

                status, msg_data = self._imap.fetch(uid_str, "(RFC822)")
                if status != "OK" or not msg_data or not msg_data[0]:
                    continue

                raw_email = msg_data[0][1]
                if isinstance(raw_email, bytes):
                    msg = email_lib.message_from_bytes(raw_email)
                else:
                    msg = email_lib.message_from_string(str(raw_email))

                # Header'lari coz
                from_header = _decode_email_header(msg.get("From", ""))
                subject = _decode_email_header(msg.get("Subject", "(Konusuz)"))
                date_str = msg.get("Date", "")

                # Gonderici e-posta adresini ayikla (chat_id olarak kullanilir)
                import re
                sender_match = re.search(r"<([^>]+)>", from_header)
                sender_email = sender_match.group(1) if sender_match else from_header.strip()

                # Mesaj icerigini ayikla
                body = _extract_text_from_message(msg)

                # Zaman damgasi
                timestamp = datetime.now(timezone.utc)
                if date_str:
                    try:
                        parsed = parsedate_to_datetime(date_str)
                        if parsed:
                            timestamp = parsed
                    except Exception:
                        pass

                # Mesaj icerigi
                text = f"{subject}\n\n{body}" if subject != "(Konusuz)" else body

                message_event = MessageEvent(
                    text=text.strip(),
                    message_type=MessageType.TEXT,
                    message_id=uid_str,
                    raw_message={
                        "from": from_header,
                        "sender_email": sender_email,
                        "subject": subject,
                        "date": date_str,
                    },
                    timestamp=timestamp,
                )

                events.append(message_event)
                self._seen_uids.add(uid_str)

        except (imaplib.IMAP4.error, OSError) as e:
            logger.error("[Email] IMAP mesaj getirme hatasi: %s", e)

        return events

    async def _poll_inbox(self) -> None:
        """Periyodik olarak IMAP inbox'ini kontrol et."""
        while self._connected:
            try:
                events = await self._fetch_new_messages()
                for event in events:
                    logger.debug(
                        "[Email] Yeni mesaj: %s",
                        event.raw_message.get("sender_email", "bilinmiyor"),
                    )
                    # Gateway tarafindan islenecek sekilde handler'a gonder
                    if self._message_handler:
                        await self._message_handler(event)
            except Exception as e:
                logger.exception("[Email] Polling sirasinda hata: %s", e)

            await asyncio.sleep(self._poll_interval)

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    async def connect(self) -> bool:
        """
        SMTP ve IMAP baglantilarini baslat.

        Returns:
            True eger her iki baglanti da basariliysa.
        """
        try:
            if not self._email_address or not self._email_password:
                logger.error("[Email] EMAIL_ADDRESS veya EMAIL_PASSWORD eksik")
                self._set_fatal_error(
                    "missing_credentials",
                    "E-posta yapilandirmasi eksik",
                    retryable=False,
                )
                return False

            # SMTP baglantisi
            smtp_ok = await self._connect_smtp()
            if not smtp_ok:
                logger.warning("[Email] SMTP baglantisi basarisiz, sadece IMAP modunda calisilacak")

            # IMAP baglantisi
            imap_ok = await self._connect_imap()
            if not imap_ok:
                logger.warning("[Email] IMAP baglantisi basarisiz, sadece SMTP modunda calisilacak")

            if not smtp_ok and not imap_ok:
                self._set_fatal_error(
                    "connection_failed",
                    "SMTP ve IMAP baglantilari basarisiz",
                    retryable=True,
                )
                return False

            self._connected = True

            # IMAP polling baslat
            if imap_ok:
                self._poll_task = asyncio.create_task(self._poll_inbox())

            logger.info("[Email] Baglanti basarili: %s", self._email_address)
            return True

        except Exception as e:
            logger.exception("[Email] Baglanti hatasi: %s", e)
            self._set_fatal_error(
                "connection_error",
                f"Email baglanti hatasi: {e}",
                retryable=True,
            )
            return False

    async def disconnect(self) -> None:
        """Email baglantilarini kapat."""
        logger.info("[Email] Baglanti kapatiliyor...")
        self._connected = False

        # Polling gorevini durdur
        if self._poll_task is not None:
            self._poll_task.cancel()
            try:
                await self._poll_task
            except asyncio.CancelledError:
                pass
            self._poll_task = None

        await self._disconnect_imap()
        await self._disconnect_smtp()

        self._connected = False

    # ------------------------------------------------------------------
    # Message sending (SMTP)
    # ------------------------------------------------------------------

    async def send(
        self,
        chat_id: str,
        content: str,
        reply_to: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SendResult:
        """
        E-posta gonder (SMTP).

        Args:
            chat_id: Alici e-posta adresi
            content: Mesaj icerigi (duz metin)
            reply_to: Yanitlanan mesajin Message-ID'si (opsiyonel)
            metadata: Ek opsiyonlar
                - subject: E-posta konusu (varsayilan: "ReYMeN'den Mesaj")
                - cc: CC adresleri (string veya liste)

        Returns:
            SendResult
        """
        recipient = chat_id.strip()
        if not recipient:
            return SendResult(False, error="Alici e-posta adresi belirtilmemis")

        if self._smtp is None:
            # SMTP yoksa yeniden baglanmayi dene
            smtp_ok = await self._connect_smtp()
            if not smtp_ok:
                return SendResult(False, error="SMTP baglantisi yok")

        subject = "ReYMeN'den Mesaj"
        cc: Optional[str] = None

        if metadata:
            subject = metadata.get("subject", subject)
            cc_val = metadata.get("cc")
            if cc_val:
                cc = cc_val if isinstance(cc_val, str) else ",".join(cc_val)

        try:
            # E-posta mesaji olustur
            msg = MIMEMultipart("alternative")
            msg["From"] = formataddr(("ReYMeN", self._email_address))
            msg["To"] = recipient
            msg["Subject"] = subject

            if cc:
                msg["Cc"] = cc

            # In-Reply-To (reply_to)
            if reply_to:
                msg["In-Reply-To"] = reply_to

            # Duz metin ve HTML versiyonlari
            plain_text = strip_markdown(content)
            msg.attach(MIMEText(plain_text, "plain", "utf-8"))
            msg.attach(MIMEText(content, "html", "utf-8"))

            # Alicilari belirle (To + CC)
            all_recipients = [recipient]
            if cc:
                all_recipients.extend(
                    [addr.strip() for addr in cc.split(",") if addr.strip()]
                )

            logger.debug(
                "[Email] Mesaj gonderiliyor: to=%s, subject=%s, len=%d",
                recipient,
                subject,
                len(content),
            )

            # SMTP uzerinden gonder
            if self._smtp is not None:
                self._smtp.sendmail(
                    self._email_address,
                    all_recipients,
                    msg.as_string(),
                )
            else:
                return SendResult(False, error="SMTP baglantisi yok")

            logger.info("[Email] Mesaj basariyla gonderildi: %s -> %s", self._email_address, recipient)

            return SendResult(
                success=True,
                message_id=msg.get("Message-ID", ""),
                raw_response={"to": recipient, "subject": subject},
            )

        except smtplib.SMTPException as e:
            logger.error("[Email] SMTP gonderim hatasi: %s", e)
            # Baglanti kopmus olabilir, yeniden baglanmayi dene
            self._smtp = None
            return SendResult(False, error=str(e), retryable=True)

        except Exception as e:
            logger.error("[Email] Beklenmeyen gonderim hatasi: %s", e)
            return SendResult(False, error=str(e))

    async def send_message(
        self,
        chat_id: str,
        text: str,
        *,
        reply_to: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> SendResult:
        """E-posta gonder (convenience wrapper). ``send()`` metoduna yonlendirir."""
        return await self.send(
            chat_id=chat_id,
            content=text,
            reply_to=reply_to,
            metadata=metadata,
        )

    # ------------------------------------------------------------------
    # Chat info
    # ------------------------------------------------------------------

    async def get_chat_info(self, chat_id: str) -> Dict[str, Any]:
        """
        E-posta adresi hakkinda bilgi dondur.

        Args:
            chat_id: E-posta adresi

        Returns:
            chat_id hakkinda temel bilgiler
        """
        return {
            "name": chat_id,
            "type": "dm",
            "email": chat_id,
            "platform": "email",
        }

    # ------------------------------------------------------------------
    # Message formatting
    # ------------------------------------------------------------------

    def format_message(self, content: str) -> str:
        """
        Mesaji email icin formatla.

        Email HTML formatini destekler, bu nedenle markdown temel
        HTML'e donusturulebilir. Simdilik duz metin olarak gonderiyoruz.
        """
        return content
