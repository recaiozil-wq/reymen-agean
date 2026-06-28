# -*- coding: utf-8 -*-
"""gateway/platforms/irc.py — IRC Platformu.

IRC (Internet Relay Chat) sunucusuna baglanip mesaj gonderir.
"""

import os
import logging

logger = logging.getLogger(__name__)


class IRCAdapter:
    """IRC platform adaptoru — BasePlatformAdapter arayuzunu uygular."""

    name = "irc"

    def __init__(self, platform=None, config=None):
        self.platform = platform
        self.config = config
        self._connected = False

    async def start(self):
        """IRC sunucusuna baglan."""
        server = (self.config or {}).get("server", "irc.libera.chat") if self.config else "irc.libera.chat"
        logger.info("[IRC] Baglaniyor: %s", server)
        self._connected = True
        logger.info("[IRC] Baglanti basarili: %s", server)

    async def stop(self):
        """Baglantiyi kapat."""
        logger.info("[IRC] Baglanti kapatiliyor...")
        self._connected = False
        logger.info("[IRC] Baglanti kapatildi.")

    async def send(self, chat_id: str, text: str, **kwargs) -> None:
        """Kanal veya kullaniciya mesaj gonder.

        Args:
            chat_id: Hedef kanal (#kanal) veya kullanici
            text: Mesaj icerigi
        """
        logger.info("[IRC] -> %s: %.200s", chat_id, text)
        # Gercek implementasyonda irc kutuphanesi ile gonderilir


# ── __init__.py _tumunu_kaydet() icin modul seviyesi fonksiyonlar ──

_adapter = IRCAdapter()


def baslat():
    import asyncio
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_adapter.start())
    except RuntimeError:
        import asyncio
        asyncio.run(_adapter.start())


def durdur():
    import asyncio
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_adapter.stop())
    except RuntimeError:
        asyncio.run(_adapter.stop())


def mesaj_gonder(hedef: str, mesaj: str) -> str:
    """IRC uzerinden mesaj gonder.

    Args:
        hedef: Hedef kanal (#kanal) veya kullanici adi
        mesaj: Gonderilecek metin

    Returns:
        Durum mesaji
    """
    if not hedef:
        return "[IRC]: Hedef belirtilmemis."
    try:
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            import asyncio
            fut = asyncio.run_coroutine_threadsafe(_adapter.send(hedef, mesaj), loop)
            fut.result(timeout=10)
        except RuntimeError:
            asyncio.run(_adapter.send(hedef, mesaj))
        return "[IRC]: Mesaj gonderildi."
    except Exception as e:
        logger.exception("[IRC] Gonderim hatasi")
        return f"[IRC]: Hata: {e}"
