# -*- coding: utf-8 -*-
"""gateway/platforms/telegram_network.py — Telegram Gelismis Ag Yonetimi.

Telethon istemcisi ile oturum yonetimi, baglanti durumu, yeniden baglanma.
Telethon yoksa graceful degrade.
"""

import os
import logging
import asyncio

logger = logging.getLogger(__name__)

try:
    from telethon import TelegramClient
    _TELETHON_OK = True
except ImportError:
    _TELETHON_OK = False

try:
    import requests
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

_client = None
_session_name = "gateway_telegram"


def _get_client() -> object:
    """TelegramClient ornegi al veya olustur (sadece Telethon varsa)."""
    global _client
    if not _TELETHON_OK:
        return None
    if _client is not None:
        return _client

    api_id = os.environ.get("TELEGRAM_API_ID", "")
    api_hash = os.environ.get("TELEGRAM_API_HASH", "")
    session_file = os.environ.get("TELEGRAM_SESSION", _session_name)

    if not api_id or not api_hash:
        logger.warning("TELEGRAM_API_ID veya TELEGRAM_API_HASH ayarlanmamis.")
        return None

    try:
        _client = TelegramClient(session_file, int(api_id), api_hash)
        return _client
    except Exception as e:
        logger.error("TelegramClient olusturulamadi: %s", e)
        return None


async def _async_send(hedef: str, mesaj: str, **kwargs) -> dict:
    """Async olarak mesaj gonder."""
    client = _get_client()
    if client is None:
        return {"durum": "hata", "hata": "Telethon kullanilamiyor veya yapilandirma eksik."}

    try:
        if not client.is_connected():
            await client.connect()

        if not await client.is_user_authorized():
            phone = os.environ.get("TELEGRAM_PHONE", "")
            if phone:
                await client.send_code_request(phone)
                code = kwargs.get("code", "")
                if code:
                    await client.sign_in(phone, code)
                else:
                    return {"durum": "hata", "hata": "Kod gerekli. 'code' parametresi ile gonderin."}
            else:
                return {"durum": "hata", "hata": "TELEGRAM_PHONE ayarlanmamis."}

        # Hedef bir kullanici, grup veya kanal olabilir
        entity = await client.get_entity(hedef)
        await client.send_message(entity, mesaj, **kwargs)
        return {"durum": "basarili", "hedef": hedef}
    except Exception as e:
        return {"durum": "hata", "hata": str(e)}


def send_message(hedef: str, mesaj: str, **kwargs) -> dict:
    """Telegram mesaji gonderir.

    Telethon istemcisi ile oturum acar ve mesaji gonderir.
    Telethon yoksa HTTP bot API uzerinden gonderir.

    Args:
        hedef: Kullanici, grup veya kanal ID'si / username
        mesaj: Mesaj icerigi

    Keyword Args:
        code: Telefon kodu (oturum yoksa gerekli)
        token: Bot token (HTTP modunda kullanilir, env'den TELEGRAM_BOT_TOKEN)

    Returns:
        dict: {"durum": "basarili", ...} veya {"durum": "hata", ...}
    """
    if _TELETHON_OK:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(_async_send(hedef, mesaj, **kwargs))
            finally:
                loop.close()
        except Exception as e:
            return {"durum": "hata", "hata": f"Telethon async hata: {e}"}

    # Degrade: HTTP bot API
    if not _REQUESTS_OK:
        return {"durum": "hata", "hata": "requests kutuphanesi yok. Telethon da mevcut degil."}

    token = kwargs.get("token") or os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        return {"durum": "hata", "hata": "TELEGRAM_BOT_TOKEN ayarlanmamis (HTTP modu)."}

    try:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": hedef, "text": mesaj[:4096]},
            timeout=10,
        )
        data = r.json()
        if data.get("ok"):
            return {"durum": "basarili", "mesaj_id": data.get("result", {}).get("message_id", "")}
        return {"durum": "hata", "hata": f"Telegram API: {data.get('description', 'bilinmiyor')}"}
    except Exception as e:
        return {"durum": "hata", "hata": str(e)}


def ping() -> bool:
    """Telegram baglantisini kontrol eder.

    Telethon varsa istemci baglantisini dener,
    yoksa bot API uzerinden getMe cagirir.

    Returns:
        bool: Baglanti basarili ise True
    """
    if _TELETHON_OK:
        client = _get_client()
        if client is None:
            return False
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                if not client.is_connected():
                    loop.run_until_complete(client.connect())
                return loop.run_until_complete(client.is_user_authorized())
            finally:
                loop.close()
        except Exception:
            return False

    # HTTP modu
    if not _REQUESTS_OK:
        return False
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        return False
    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        return r.status_code == 200 and r.json().get("ok", False)
    except Exception:
        return False
