# -*- coding: utf-8 -*-
"""plugins/platforms/ntfy.py — ntfy Bildirim Platformu.

ntfy (ntfy.sh) uzerinden push bildirimleri gonderimi saglar.
Opsiyonel bagimlilik: requests
"""

import logging

logger = logging.getLogger(__name__)

PLUGIN_ADI = "ntfy"
PLUGIN_VERSIYON = "1.0.0"
PLUGIN_ACIKLAMA = "ntfy push bildirim platformu"

try:
    import requests
    NTFY_MEVCUT = True
except ImportError:
    NTFY_MEVCUT = False
    logger.debug("requests kutuphanesi yuklu degil")


def motor_kaydet(motor):
    """ntfy pluginini motor'a kaydeder.

    Args:
        motor: Motor ornegi
    """
    if not NTFY_MEVCUT:
        logger.warning("[Plugin:ntfy] requests kutuphanesi bulunamadi, plugin atlandi.")
        return

    def ntfy_bildirim_gonder(args):
        """ntfy.sh uzerinden push bildirimi gonder."""
        try:
            konu = args.get("konu", "")
            mesaj = args.get("mesaj", "")
            baslik = args.get("baslik", "ReYMeN Bildirim")
            oncelik = args.get("oncelik", "default")
            if not konu or not mesaj:
                return "[ntfy] konu ve mesaj gerekli."
            payload = {
                "topic": konu,
                "message": mesaj,
                "title": baslik,
                "priority": oncelik
            }
            resp = requests.post("https://ntfy.sh", json=payload, timeout=10)
            resp.raise_for_status()
            return f"[ntfy] Bildirim gonderildi: {konu}"
        except Exception as e:
            return f"[ntfy] Hata: {e}"

    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet("NTFY_BILDIRIM_GONDER", ntfy_bildirim_gonder, "ntfy.sh push bildirimi gonderir")
    elif hasattr(motor, "_registry") and motor._registry:
        motor._registry.kaydet("NTFY_BILDIRIM_GONDER", ntfy_bildirim_gonder)

    logger.info("[Plugin:ntfy] ntfy platformu kayit edildi.")
