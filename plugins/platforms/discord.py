# -*- coding: utf-8 -*-
"""plugins/platforms/discord.py — Discord Bot Platformu.

Discord bot uzerinden mesajlasma ve komut yonetimi saglar.
Opsiyonel bagimlilik: discord.py
"""

import logging

logger = logging.getLogger(__name__)

PLUGIN_ADI = "discord"
PLUGIN_VERSIYON = "1.0.0"
PLUGIN_ACIKLAMA = "Discord bot platform entegrasyonu"

try:
    import discord
    from discord.ext import commands
    DISCORD_MEVCUT = True
except ImportError:
    DISCORD_MEVCUT = False
    logger.debug("discord.py kutuphanesi yuklu degil")


def motor_kaydet(motor):
    """Discord pluginini motor'a kaydeder.

    Args:
        motor: Motor ornegi
    """
    if not DISCORD_MEVCUT:
        logger.warning("[Plugin:discord] discord.py kutuphanesi bulunamadi, plugin atlandi.")
        return

    def discord_mesaj_gonder(args):
        """Discord kanalina mesaj gonder."""
        try:
            import asyncio
            token = args.get("token", "")
            kanal_id = args.get("kanal_id", "")
            mesaj = args.get("mesaj", "")
            if not token or not kanal_id or not mesaj:
                return "[Discord] token, kanal_id ve mesaj gerekli."
            intents = discord.Intents.default()
            client = discord.Client(intents=intents)

            async def send():
                await client.wait_until_ready()
                kanal = client.get_channel(int(kanal_id))
                if kanal:
                    await kanal.send(mesaj)
                await client.close()

            client.loop.create_task(send())
            client.run(token, log_handler=None)
            return f"[Discord] Mesaj gonderildi: {kanal_id}"
        except Exception as e:
            return f"[Discord] Hata: {e}"

    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet("DISCORD_MESAJ_GONDER", discord_mesaj_gonder, "Discord kanalina mesaj gonderir")
    elif hasattr(motor, "_registry") and motor._registry:
        motor._registry.kaydet("DISCORD_MESAJ_GONDER", discord_mesaj_gonder)

    logger.info("[Plugin:discord] Discord platformu kayit edildi.")
