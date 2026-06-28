# -*- coding: utf-8 -*-
"""plugins/web/brave.py — Brave Search API Plugin.

Brave Search API uzerinden web aramasi yapar.
Opsiyonel bagimlilik: requests
"""

import logging

logger = logging.getLogger(__name__)

PLUGIN_ADI = "brave"
PLUGIN_VERSIYON = "1.0.0"
PLUGIN_ACIKLAMA = "Brave Search API web arama plugin"

try:
    import requests
    BRAVE_MEVCUT = True
except ImportError:
    BRAVE_MEVCUT = False
    logger.debug("requests kutuphanesi yuklu degil")


def motor_kaydet(motor):
    """Brave Search pluginini motor'a kaydeder.

    Args:
        motor: Motor ornegi
    """
    if not BRAVE_MEVCUT:
        logger.warning("[Plugin:brave] requests kutuphanesi bulunamadi, plugin atlandi.")
        return

    def brave_ara(args):
        """Brave Search API ile arama yap."""
        try:
            api_key = args.get("api_key", "")
            sorgu = args.get("sorgu", args.get("q", ""))
            count = args.get("count", 5)
            if not api_key:
                return "[Brave] api_key gerekli (BRAVE_API_KEY)."
            if not sorgu:
                return "[Brave] sorgu gerekli."
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": api_key
            }
            params = {"q": sorgu, "count": count}
            resp = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params,
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()
            sonuclar = data.get("web", {}).get("results", [])
            if not sonuclar:
                return f"[Brave] '{sorgu}' icin sonuc bulunamadi."
            satirlar = []
            for i, r in enumerate(sonuclar[:count]):
                baslik = r.get("title", "Basliksiz")
                url = r.get("url", "")
                aciklama = r.get("description", "")
                satirlar.append(f"{i+1}. {baslik}\n   {url}\n   {aciklama}")
            return "[Brave] Sonuclar:\n" + "\n\n".join(satirlar)
        except Exception as e:
            return f"[Brave] Arama hatasi: {e}"

    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet("BRAVE_ARA", brave_ara, "Brave Search API ile web aramasi yapar")
    elif hasattr(motor, "_registry") and motor._registry:
        motor._registry.kaydet("BRAVE_ARA", brave_ara)

    logger.info("[Plugin:brave] Brave Search plugin kayit edildi.")
