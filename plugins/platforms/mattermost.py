# -*- coding: utf-8 -*-
"""plugins/platforms/mattermost.py — Mattermost Platformu.

Mattermost uzerinden mesajlasma ve bildirim gonderimi saglar.
Opsiyonel bagimlilik: requests
"""

import logging

logger = logging.getLogger(__name__)

PLUGIN_ADI = "mattermost"
PLUGIN_VERSIYON = "1.0.0"
PLUGIN_ACIKLAMA = "Mattermost platform entegrasyonu"

try:
    import requests
    MATTERMOST_MEVCUT = True
except ImportError:
    MATTERMOST_MEVCUT = False
    logger.debug("requests kutuphanesi yuklu degil")


def motor_kaydet(motor):
    """Mattermost pluginini motor'a kaydeder.

    Args:
        motor: Motor ornegi
    """
    if not MATTERMOST_MEVCUT:
        logger.warning("[Plugin:mattermost] requests kutuphanesi bulunamadi, plugin atlandi.")
        return

    def mattermost_mesaj_gonder(args):
        """Mattermost kanalina mesaj gonder (webhook ile)."""
        try:
            webhook_url = args.get("webhook_url", "")
            mesaj = args.get("mesaj", "")
            if not webhook_url or not mesaj:
                return "[Mattermost] webhook_url ve mesaj gerekli."
            payload = {"text": mesaj}
            resp = requests.post(webhook_url, json=payload, timeout=10)
            resp.raise_for_status()
            return f"[Mattermost] Mesaj gonderildi."
        except Exception as e:
            return f"[Mattermost] Hata: {e}"

    def mattermost_api_sorgula(args):
        """Mattermost REST API uzerinden islem yap."""
        try:
            sunucu = args.get("sunucu", "")
            token = args.get("token", "")
            ucsun = args.get("ucsun", "api/v4/users")
            if not sunucu or not token:
                return "[Mattermost] sunucu ve token gerekli."
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{sunucu.rstrip('/')}/{ucsun.lstrip('/')}"
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            return str(resp.json()[:2])
        except Exception as e:
            return f"[Mattermost] API hatasi: {e}"

    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet("MATTERMOST_MESAJ_GONDER", mattermost_mesaj_gonder, "Mattermost webhook ile mesaj gonderir")
        motor._plugin_arac_kaydet("MATTERMOST_API", mattermost_api_sorgula, "Mattermost API sorgusu yapar")
    elif hasattr(motor, "_registry") and motor._registry:
        motor._registry.kaydet("MATTERMOST_MESAJ_GONDER", mattermost_mesaj_gonder)
        motor._registry.kaydet("MATTERMOST_API", mattermost_api_sorgula)

    logger.info("[Plugin:mattermost] Mattermost platformu kayit edildi.")
