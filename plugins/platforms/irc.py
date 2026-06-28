# -*- coding: utf-8 -*-
"""plugins/platforms/irc.py — IRC Bot Platformu.

IRC uzerinden mesajlasma ve bot yonetimi saglar.
Opsiyonel bagimlilik: irc (irc.bot)
"""

import logging

logger = logging.getLogger(__name__)

PLUGIN_ADI = "irc"
PLUGIN_VERSIYON = "1.0.0"
PLUGIN_ACIKLAMA = "IRC platform entegrasyonu"

try:
    import irc.client
    from irc.client import SimpleIRCClient
    IRC_MEVCUT = True
except ImportError:
    IRC_MEVCUT = False
    logger.debug("irc kutuphanesi yuklu degil")


def motor_kaydet(motor):
    """IRC pluginini motor'a kaydeder.

    Args:
        motor: Motor ornegi
    """
    if not IRC_MEVCUT:
        logger.warning("[Plugin:irc] irc kutuphanesi bulunamadi, plugin atlandi.")
        return

    def irc_mesaj_gonder(args):
        """IRC kanalina mesaj gonder."""
        try:
            sunucu = args.get("sunucu", "irc.libera.chat")
            port = args.get("port", 6667)
            kanal = args.get("kanal", "")
            mesaj = args.get("mesaj", "")
            nick = args.get("nick", "ReYMeNBot")
            if not kanal or not mesaj:
                return "[IRC] kanal ve mesaj gerekli."
            if not kanal.startswith("#"):
                kanal = "#" + kanal
            client = SimpleIRCClient()
            client.connect(sunucu, port, nick)
            client.connection.join(kanal)
            client.connection.privmsg(kanal, mesaj)
            client.connection.quit("Gorusecegiz")
            return f"[IRC] Mesaj gonderildi: {kanal}"
        except Exception as e:
            return f"[IRC] Hata: {e}"

    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet("IRC_MESAJ_GONDER", irc_mesaj_gonder, "IRC kanalina mesaj gonderir")
    elif hasattr(motor, "_registry") and motor._registry:
        motor._registry.kaydet("IRC_MESAJ_GONDER", irc_mesaj_gonder)

    logger.info("[Plugin:irc] IRC platformu kayit edildi.")
