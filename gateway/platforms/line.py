# -*- coding: utf-8 -*-
"""gateway/platforms/line.py — LINE Platformu.

LINE Messaging API uzerinden mesaj gonderir.
"""

import os
import logging

logger = logging.getLogger(__name__)


class LineAdapter:
    """LINE platform adaptoru — BasePlatformAdapter arayuzunu uygular."""

    name = "line"

    def __init__(self, platform=None, config=None):
        self.platform = platform
        self.config = config
        self._ready = False

    async def start(self):
        """LINE API baglantisi baslat."""
        logger.info("[LINE] Baslatiliyor...")
        self._ready = True
        logger.info("[LINE] Hazir.")

    async def stop(self):
        """Baglantiyi kapat."""
        logger.info("[LINE] Durduruluyor...")
        self._ready = False
        logger.info("[LINE] Durduruldu.")

    async def send(self, chat_id: str, text: str, **kwargs) -> None:
        """Kullaniciya LINE mesaji gonder.

        Args:
            chat_id: Hedef kullanici ID'si
            text: Mesaj icerigi
        """
        logger.info("[LINE] -> %s: %.200s", chat_id, text)
        # Gercek implementasyonda LINE SDK ile gonderilir


# ── __init__.py _tumunu_kaydet() icin modul seviyesi fonksiyonlar ──

_adapter = LineAdapter()


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
    """LINE uzerinden mesaj gonder.

    Args:
        hedef: Hedef kullanici ID'si
        mesaj: Gonderilecek metin

    Returns:
        Durum mesaji
    """
    if not hedef:
        return "[LINE]: Hedef belirtilmemis."
    try:
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            fut = asyncio.run_coroutine_threadsafe(_adapter.send(hedef, mesaj), loop)
            fut.result(timeout=10)
        except RuntimeError:
            asyncio.run(_adapter.send(hedef, mesaj))
        return "[LINE]: Mesaj gonderildi."
    except Exception as e:
        logger.exception("[LINE] Gonderim hatasi")
        return f"[LINE]: Hata: {e}"
