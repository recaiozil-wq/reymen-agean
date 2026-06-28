# -*- coding: utf-8 -*-
"""gateway/platforms/telegram.py — Telegram Bot Platformu.

Telegram_network.py'den farkli: basit bot API, webhook tabanli.
.env'den TELEGRAM_BOT_TOKEN okur.
"""

import os
import logging

try:
    import requests
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

logger = logging.getLogger(__name__)

_API_BASE = "https://api.telegram.org/bot"


def _token_al() -> str:
    """Ortam degiskeninden bot token'ini al."""
    return os.environ.get("TELEGRAM_BOT_TOKEN", "")


def send_message(hedef: str, mesaj: str, **kwargs) -> dict:
    """Telegram bot API ile mesaj gonder.

    Args:
        hedef: Chat ID (kullanici, grup veya kanal)
        mesaj: Gonderilecek metin (max 4096 karakter)

    Keyword Args:
        parse_mode: Mesaj formatı ("HTML" / "MarkdownV2" / varsayilan: plain)
        disable_web_page_preview: Baglanti onizlemeyi kapat (bool)
        disable_notification: Sessiz gonder (bool)
        reply_to_message_id: Yanitlanacak mesaj ID'si
        reply_markup: Inline klavye veya tus takimi (dict)

    Returns:
        dict: {"durum": "basarili", "mesaj_id": ...} veya {"durum": "hata", "hata": ...}
    """
    token = _token_al()
    if not token:
        return {"durum": "hata", "hata": "TELEGRAM_BOT_TOKEN ayarlanmamis."}

    if not _REQUESTS_OK:
        return {"durum": "hata", "hata": "requests kutuphanesi yok."}

    # Istege bagli parametreler
    payload = {
        "chat_id": hedef,
        "text": mesaj[:4096],
    }

    parse_mode = kwargs.get("parse_mode")
    if parse_mode and parse_mode.upper() in ("HTML", "MARKDOWNV2"):
        payload["parse_mode"] = parse_mode.upper()

    if kwargs.get("disable_web_page_preview"):
        payload["disable_web_page_preview"] = True

    if kwargs.get("disable_notification"):
        payload["disable_notification"] = True

    reply_id = kwargs.get("reply_to_message_id")
    if reply_id is not None:
        payload["reply_to_message_id"] = reply_id

    reply_markup = kwargs.get("reply_markup")
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup

    try:
        r = requests.post(
            f"{_API_BASE}{token}/sendMessage",
            json=payload,
            timeout=15,
        )
        data = r.json()

        if data.get("ok"):
            result = data.get("result", {})
            return {
                "durum": "basarili",
                "mesaj_id": result.get("message_id", ""),
                "chat_id": result.get("chat", {}).get("id", ""),
            }

        # API hata aciklamasi
        hata_kodu = data.get("error_code", "")
        hata_msg = data.get("description", "bilinmiyor")
        return {"durum": "hata", "hata": f"Telegram API ({hata_kodu}): {hata_msg}"}

    except requests.exceptions.Timeout:
        return {"durum": "hata", "hata": "Telegram API zaman asimi."}
    except requests.exceptions.ConnectionError:
        return {"durum": "hata", "hata": "Telegram API baglanti hatasi."}
    except Exception as e:
        return {"durum": "hata", "hata": str(e)}


def send_photo(hedef: str, foto_url: str, altyazi: str = "", **kwargs) -> dict:
    """Telegram'a foto gonder.

    Args:
        hedef: Chat ID
        foto_url: Foto URL'si veya file_id
        altyazi: Foto alt yazisi (opsiyonel)

    Returns:
        dict: {"durum": "basarili", ...} veya {"durum": "hata", ...}
    """
    token = _token_al()
    if not token:
        return {"durum": "hata", "hata": "TELEGRAM_BOT_TOKEN ayarlanmamis."}
    if not _REQUESTS_OK:
        return {"durum": "hata", "hata": "requests kutuphanesi yok."}

    try:
        payload = {
            "chat_id": hedef,
            "photo": foto_url,
        }
        if altyazi:
            payload["caption"] = altyazi[:1024]

        r = requests.post(
            f"{_API_BASE}{token}/sendPhoto",
            json=payload,
            timeout=30,
        )
        data = r.json()
        if data.get("ok"):
            return {"durum": "basarili", "mesaj_id": data.get("result", {}).get("message_id", "")}
        return {"durum": "hata", "hata": f"Telegram API: {data.get('description', '')}"}
    except Exception as e:
        return {"durum": "hata", "hata": str(e)}


def set_webhook(url: str, **kwargs) -> dict:
    """Telegram bot webhook'u ayarla.

    Args:
        url: Webhook URL'si (https zorunlu)

    Keyword Args:
        allowed_updates: Izlenecek guncelleme tipleri (list)
        drop_pending_updates: Bekleyen guncellemeleri temizle (bool)
        max_connections: Maksimum baglanti sayisi (int)

    Returns:
        dict: {"durum": "basarili", ...} veya {"durum": "hata", ...}
    """
    token = _token_al()
    if not token:
        return {"durum": "hata", "hata": "TELEGRAM_BOT_TOKEN ayarlanmamis."}
    if not _REQUESTS_OK:
        return {"durum": "hata", "hata": "requests kutuphanesi yok."}

    try:
        payload = {"url": url}
        if "allowed_updates" in kwargs:
            payload["allowed_updates"] = kwargs["allowed_updates"]
        if "drop_pending_updates" in kwargs:
            payload["drop_pending_updates"] = kwargs["drop_pending_updates"]
        if "max_connections" in kwargs:
            payload["max_connections"] = kwargs["max_connections"]

        r = requests.post(
            f"{_API_BASE}{token}/setWebhook",
            json=payload,
            timeout=10,
        )
        data = r.json()
        if data.get("ok"):
            return {"durum": "basarili", "aciklama": data.get("description", "")}
        return {"durum": "hata", "hata": f"Webhook ayarlanamadi: {data.get('description', '')}"}
    except Exception as e:
        return {"durum": "hata", "hata": str(e)}


def delete_webhook(**kwargs) -> dict:
    """Telegram bot webhook'unu kaldir.

    Returns:
        dict: {"durum": "basarili", ...} veya {"durum": "hata", ...}
    """
    token = _token_al()
    if not token:
        return {"durum": "hata", "hata": "TELEGRAM_BOT_TOKEN ayarlanmamis."}
    if not _REQUESTS_OK:
        return {"durum": "hata", "hata": "requests kutuphanesi yok."}

    try:
        payload = {}
        if "drop_pending_updates" in kwargs:
            payload["drop_pending_updates"] = kwargs["drop_pending_updates"]

        r = requests.post(
            f"{_API_BASE}{token}/deleteWebhook",
            json=payload if payload else None,
            timeout=10,
        )
        data = r.json()
        if data.get("ok"):
            return {"durum": "basarili"}
        return {"durum": "hata", "hata": f"Webhook silinemedi: {data.get('description', '')}"}
    except Exception as e:
        return {"durum": "hata", "hata": str(e)}


def get_webhook_info() -> dict:
    """Mevcut webhook yapilandirmasini sorgula.

    Returns:
        dict: {"durum": "basarili", "info": {...}} veya {"durum": "hata", ...}
    """
    token = _token_al()
    if not token:
        return {"durum": "hata", "hata": "TELEGRAM_BOT_TOKEN ayarlanmamis."}
    if not _REQUESTS_OK:
        return {"durum": "hata", "hata": "requests kutuphanesi yok."}

    try:
        r = requests.get(f"{_API_BASE}{token}/getWebhookInfo", timeout=10)
        data = r.json()
        if data.get("ok"):
            return {"durum": "basarili", "info": data.get("result", {})}
        return {"durum": "hata", "hata": data.get("description", "")}
    except Exception as e:
        return {"durum": "hata", "hata": str(e)}


def parse_message(raw: dict) -> dict:
    """Telegram webhook'tan gelen mesaji normalize et.

    Args:
        raw: Telegram'dan gelen Update objesi

    Returns:
        dict: {"gonderen": ..., "metin": ..., "platform": "telegram", ...}
    """
    try:
        message = raw.get("message") or raw.get("edited_message") or {}
        chat = message.get("chat", {})
        from_user = message.get("from", {})

        metin = (
            message.get("text")
            or message.get("caption")
            or ""
        )

        return {
            "gonderen": str(from_user.get("id", "")),
            "gonderen_ad": from_user.get("first_name", ""),
            "gonderen_kullanici": from_user.get("username", ""),
            "metin": metin,
            "chat_id": str(chat.get("id", "")),
            "chat_tip": chat.get("type", ""),
            "mesaj_id": message.get("message_id", 0),
            "platform": "telegram",
            "ham": raw,
        }
    except Exception:
        return {"gonderen": "", "metin": "", "platform": "telegram", "ham": raw}


def ping() -> bool:
    """Telegram bot API baglantisini kontrol et.

    getMe API'sini cagirarak token'in gecerli olup olmadigini kontrol eder.

    Returns:
        bool: Bot API erisilebilir ve token gecerli ise True
    """
    token = _token_al()
    if not token:
        return False
    if not _REQUESTS_OK:
        return False

    try:
        r = requests.get(f"{_API_BASE}{token}/getMe", timeout=10)
        return r.status_code == 200 and r.json().get("ok", False)
    except Exception:
        return False


# Gateway platform kaydı için standart alias'lar
def baslat():
    """Platform başlatma — Telegram için no-op (webhook modeli kullanır)."""
    pass


def durdur():
    """Platform durdurma — Telegram için no-op."""
    pass


def mesaj_gonder(hedef: str, mesaj: str) -> dict:
    """gateway.platforms standart arayüzü — send_message'ı dict olarak döndür."""
    return send_message(hedef, mesaj)


def edit_message(chat_id: str, message_id: int, new_text: str, **kwargs) -> dict:
    """Telegram mesajını düzenle.

    Args:
        chat_id: Chat ID
        message_id: Düzenlenecek mesaj ID'si
        new_text: Yeni metin

    Returns:
        dict: {"durum": "basarili"} veya {"durum": "hata", "hata": ...}
    """
    token = _token_al()
    if not token:
        return {"durum": "hata", "hata": "TELEGRAM_BOT_TOKEN ayarlanmamis."}
    if not _REQUESTS_OK:
        return {"durum": "hata", "hata": "requests kutuphanesi yok."}

    try:
        payload: dict = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": new_text[:4096],
        }
        parse_mode = kwargs.get("parse_mode")
        if parse_mode:
            payload["parse_mode"] = parse_mode

        r = requests.post(
            f"{_API_BASE}{token}/editMessageText",
            json=payload,
            timeout=15,
        )
        data = r.json()

        if data.get("ok"):
            return {
                "durum": "basarili",
                "mesaj_id": data.get("result", {}).get("message_id", message_id),
            }

        desc = data.get("description", "")
        if "message is not modified" in desc.lower():
            return {"durum": "basarili", "degismedi": True}

        return {"durum": "hata", "hata": f"Telegram API: {desc}"}
    except Exception as e:
        return {"durum": "hata", "hata": str(e)}


def set_reaction(chat_id: str, message_id: int, emoji: str) -> dict:
    """Telegram mesajına emoji tepkisi ekle.

    Args:
        chat_id: Chat ID
        message_id: Tepki verilecek mesaj ID'si
        emoji: Emoji karakteri (örn. '👍')

    Returns:
        dict: {"durum": "basarili"} veya {"durum": "hata", ...}
    """
    token = _token_al()
    if not token:
        return {"durum": "hata", "hata": "TELEGRAM_BOT_TOKEN ayarlanmamis."}
    if not _REQUESTS_OK:
        return {"durum": "hata", "hata": "requests kutuphanesi yok."}

    try:
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "reaction": [{"type": "emoji", "emoji": emoji}],
        }
        r = requests.post(
            f"{_API_BASE}{token}/setMessageReaction",
            json=payload,
            timeout=15,
        )
        data = r.json()
        if data.get("ok"):
            return {"durum": "basarili"}
        return {"durum": "hata", "hata": data.get("description", "")}
    except Exception as e:
        return {"durum": "hata", "hata": str(e)}


def send_stream(chat_id: str, text: str, chunk_size: int = 4000, **kwargs) -> dict:
    """Uzun metni Telegram'a chunk'lar halinde gönder.

    Kısa mesajlar direkt gönderilir; uzunlar ilk mesaj + edit zinciriyle iletilir.

    Args:
        chat_id: Chat ID
        text: Gönderilecek metin
        chunk_size: Chunk boyutu (max 4096)

    Returns:
        dict: {"durum": "basarili", "chunk_sayisi": N} veya {"durum": "hata", ...}
    """
    if not text:
        return {"durum": "hata", "hata": "Bos metin."}

    safe_chunk = min(chunk_size, 4096)
    chunks = [text[i:i + safe_chunk] for i in range(0, len(text), safe_chunk)]

    if len(chunks) == 1:
        sonuc = send_message(chat_id, chunks[0], **kwargs)
        sonuc.setdefault("chunk_sayisi", 1)
        return sonuc

    first = send_message(chat_id, chunks[0], **kwargs)
    if first.get("durum") == "hata":
        return first

    message_id = first.get("mesaj_id")
    accumulated = chunks[0]

    for chunk in chunks[1:]:
        try:
            import time as _t
            _t.sleep(0.1)
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")
        accumulated += chunk
        if message_id:
            edit_result = edit_message(chat_id, message_id, accumulated[:4096])
            if edit_result.get("durum") == "hata" and not edit_result.get("degismedi"):
                new_msg = send_message(chat_id, chunk, **kwargs)
                if new_msg.get("durum") == "basarili":
                    message_id = new_msg.get("mesaj_id")
                    accumulated = chunk

    return {"durum": "basarili", "mesaj_id": message_id, "chunk_sayisi": len(chunks)}


class TelegramAdapter:
    """Telegram platform adaptörü — gateway/run.py ve testler için."""

    platform = "telegram"

    def __init__(self, config=None):
        self.platform = "telegram"
        self.config = config
        self._bot = None

    def _compile_mention_patterns(self) -> list:
        """Bot @mention regex pattern'lerini derle; bot yoksa boş liste."""
        if not self._bot:
            return []
        try:
            username = getattr(self._bot, "username", None)
            if username:
                import re
                return [re.compile(rf"@{re.escape(username)}", re.IGNORECASE)]
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")
        return []

    def _telegram_allowed_chats(self) -> set:
        """Konfigürasyondaki izinli chat ID setini döndür."""
        if self.config is None:
            return set()
        extra = getattr(self.config, "extra", {}) or {}
        chats = extra.get("allowed_chats", [])
        return set(chats) if chats else set()

    def send_message(self, hedef: str, mesaj: str, **kwargs) -> dict:
        return send_message(hedef, mesaj, **kwargs)

    def ping(self) -> bool:
        return ping()

    def parse_message(self, raw: dict, **kwargs) -> dict:
        return parse_message(raw)

    def baslat(self):
        baslat()

    def durdur(self):
        durdur()
