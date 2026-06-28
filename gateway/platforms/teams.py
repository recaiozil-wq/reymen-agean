# -*- coding: utf-8 -*-
"""gateway/platforms/teams.py — Microsoft Teams Platformu.

Microsoft Teams webhook / Graph API uzerinden mesaj gonderir.
"""

import os
import logging

logger = logging.getLogger(__name__)


class TeamsAdapter:
    """Teams platform adaptoru — BasePlatformAdapter arayuzunu uygular."""

    name = "teams"

    def __init__(self, platform=None, config=None):
        self.platform = platform
        self.config = config
        self._ready = False

    async def start(self):
        """Teams API baglantisini baslat."""
        logger.info("[Teams] Baslatiliyor...")
        self._ready = True
        logger.info("[Teams] Hazir.")

    async def stop(self):
        """Baglantiyi kapat."""
        logger.info("[Teams] Durduruluyor...")
        self._ready = False
        logger.info("[Teams] Durduruldu.")

    async def send(self, chat_id: str, text: str, **kwargs) -> None:
        """Teams kanalina veya kullaniciya mesaj gonder.

        Args:
            chat_id: Hedef kanal/webhook URL'si veya kullanici ID'si
            text: Mesaj icerigi
        """
        logger.info("[Teams] -> %s: %.200s", chat_id, text)
        # Gercek implementasyonda webhook veya Graph API ile gonderilir


# ── __init__.py _tumunu_kaydet() icin modul seviyesi fonksiyonlar ──

_adapter = TeamsAdapter()


def baslat():
    import asyncio
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_adapter.start())
    except RuntimeError:
        asyncio.run(_adapter.start())


def durdur():
    import asyncio
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_adapter.stop())
    except RuntimeError:
        asyncio.run(_adapter.stop())


def mesaj_gonder(hedef: str, mesaj: str) -> str:
    """Teams uzerinden mesaj gonder.

    Args:
        hedef: Hedef kanal/webhook URL'si
        mesaj: Gonderilecek metin

    Returns:
        Durum mesaji
    """
    if not hedef:
        return "[Teams]: Hedef belirtilmemis."
    try:
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            fut = asyncio.run_coroutine_threadsafe(_adapter.send(hedef, mesaj), loop)
            fut.result(timeout=10)
        except RuntimeError:
            asyncio.run(_adapter.send(hedef, mesaj))
        return "[Teams]: Mesaj gonderildi."
    except Exception as e:
        logger.exception("[Teams] Gonderim hatasi")
        return f"[Teams]: Hata: {e}"
