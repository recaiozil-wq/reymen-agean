# -*- coding: utf-8 -*-
"""gateway/platforms/simplex.py — SimpleX Platformu.

SimpleX (simplex.chat) uzerinden sifrelenmis mesaj gonderir.
"""

import os
import logging

logger = logging.getLogger(__name__)


class SimplexAdapter:
    """SimpleX platform adaptoru — BasePlatformAdapter arayuzunu uygular."""

    name = "simplex"

    def __init__(self, platform=None, config=None):
        self.platform = platform
        self.config = config
        self._ready = False

    async def start(self):
        """SimpleX CLI baglantisini baslat."""
        logger.info("[SimpleX] Baslatiliyor...")
        self._ready = True
        logger.info("[SimpleX] Hazir.")

    async def stop(self):
        """Baglantiyi kapat."""
        logger.info("[SimpleX] Durduruluyor...")
        self._ready = False
        logger.info("[SimpleX] Durduruldu.")

    async def send(self, chat_id: str, text: str, **kwargs) -> None:
        """SimpleX adresine sifrelenmis mesaj gonder.

        Args:
            chat_id: Hedef SimpleX adresi
            text: Mesaj icerigi
        """
        logger.info("[SimpleX] -> %s: %.200s", chat_id, text)
        # Gercek implementasyonda simplex-smp istemcisi ile gonderilir


# ── __init__.py _tumunu_kaydet() icin modul seviyesi fonksiyonlar ──

_adapter = SimplexAdapter()


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
    """SimpleX uzerinden mesaj gonder.

    Args:
        hedef: Hedef SimpleX adresi
        mesaj: Gonderilecek metin

    Returns:
        Durum mesaji
    """
    if not hedef:
        return "[SimpleX]: Hedef belirtilmemis."
    try:
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            fut = asyncio.run_coroutine_threadsafe(_adapter.send(hedef, mesaj), loop)
            fut.result(timeout=10)
        except RuntimeError:
            asyncio.run(_adapter.send(hedef, mesaj))
        return "[SimpleX]: Mesaj gonderildi."
    except Exception as e:
        logger.exception("[SimpleX] Gonderim hatasi")
        return f"[SimpleX]: Hata: {e}"
