# -*- coding: utf-8 -*-
"""gateway/platforms/ntfy.py — Ntfy Platformu.

ntfy.sh (veya ozel sunucu) uzerinden push bildirimi gonderir.
"""

import os
import logging

logger = logging.getLogger(__name__)


class NtfyAdapter:
    """Ntfy platform adaptoru — BasePlatformAdapter arayuzunu uygular."""

    name = "ntfy"

    def __init__(self, platform=None, config=None):
        self.platform = platform
        self.config = config
        self._ready = False

    async def start(self):
        """Ntfy istemcisini baslat."""
        logger.info("[Ntfy] Baslatiliyor...")
        self._ready = True
        logger.info("[Ntfy] Hazir.")

    async def stop(self):
        """Baglantiyi kapat."""
        logger.info("[Ntfy] Durduruluyor...")
        self._ready = False
        logger.info("[Ntfy] Durduruldu.")

    async def send(self, chat_id: str, text: str, **kwargs) -> None:
        """Ntfy kanalina push bildirimi gonder.

        Args:
            chat_id: Hedef ntfy topic (kanal) adi
            text: Bildirim icerigi
        """
        logger.info("[Ntfy] -> %s: %.200s", chat_id, text)
        # Gercek implementasyonda requests ile ntfy sunucusuna POST


# ── __init__.py _tumunu_kaydet() icin modul seviyesi fonksiyonlar ──

_adapter = NtfyAdapter()


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
    """Ntfy uzerinden push bildirimi gonder.

    Args:
        hedef: Hedef ntfy topic adi
        mesaj: Bildirim metni

    Returns:
        Durum mesaji
    """
    if not hedef:
        return "[Ntfy]: Hedef belirtilmemis."
    try:
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            fut = asyncio.run_coroutine_threadsafe(_adapter.send(hedef, mesaj), loop)
            fut.result(timeout=10)
        except RuntimeError:
            asyncio.run(_adapter.send(hedef, mesaj))
        return "[Ntfy]: Mesaj gonderildi."
    except Exception as e:
        logger.exception("[Ntfy] Gonderim hatasi")
        return f"[Ntfy]: Hata: {e}"
