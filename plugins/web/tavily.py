# -*- coding: utf-8 -*-
"""plugins/web/tavily.py — Tavily Search API Plugin.

Tavily Search API uzerinden AI-optimize web aramasi yapar.
Opsiyonel bagimlilik: tavily-python veya requests
"""

import logging

logger = logging.getLogger(__name__)

PLUGIN_ADI = "tavily"
PLUGIN_VERSIYON = "1.0.0"
PLUGIN_ACIKLAMA = "Tavily Search API web arama plugin"

# Once tavily kutuphanesini dene, yoksa requests ile REST API kullan
try:
    from tavily import TavilyClient
    TAVILY_MEVCUT = True
    TAVILY_KUTUPHANE = "tavily"
except ImportError:
    try:
        import requests
        TAVILY_MEVCUT = True
        TAVILY_KUTUPHANE = "requests"
    except ImportError:
        TAVILY_MEVCUT = False
        TAVILY_KUTUPHANE = None
        logger.debug("tavily-python / requests kutuphanesi yuklu degil")


def motor_kaydet(motor):
    """Tavily Search pluginini motor'a kaydeder.

    Args:
        motor: Motor ornegi
    """
    if not TAVILY_MEVCUT:
        logger.warning("[Plugin:tavily] tavily-python veya requests kutuphanesi bulunamadi, plugin atlandi.")
        return

    def tavily_ara(args):
        """Tavily Search API ile AI-optimize arama yap."""
        try:
            api_key = args.get("api_key", "")
            sorgu = args.get("sorgu", args.get("q", ""))
            max_results = args.get("max_results", 5)
            search_depth = args.get("search_depth", "basic")
            if not api_key:
                return "[Tavily] api_key gerekli (TAVILY_API_KEY)."
            if not sorgu:
                return "[Tavily] sorgu gerekli."

            if TAVILY_KUTUPHANE == "tavily":
                client = TavilyClient(api_key=api_key)
                response = client.search(
                    query=sorgu,
                    search_depth=search_depth,
                    max_results=max_results
                )
                sonuclar = response.get("results", [])
            else:
                # REST API ile
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                payload = {
                    "query": sorgu,
                    "search_depth": search_depth,
                    "max_results": max_results
                }
                resp = requests.post(
                    "https://api.tavily.com/search",
                    headers=headers,
                    json=payload,
                    timeout=15
                )
                resp.raise_for_status()
                data = resp.json()
                sonuclar = data.get("results", [])

            if not sonuclar:
                return f"[Tavily] '{sorgu}' icin sonuc bulunamadi."
            satirlar = []
            for i, r in enumerate(sonuclar[:max_results]):
                baslik = r.get("title", "Basliksiz")
                url = r.get("url", "")
                icerik = r.get("content", "")
                satirlar.append(f"{i+1}. {baslik}\n   {url}\n   {icerik[:200]}")
            return "[Tavily] Sonuclar:\n" + "\n\n".join(satirlar)
        except Exception as e:
            return f"[Tavily] Arama hatasi: {e}"

    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet("TAVILY_ARA", tavily_ara, "Tavily Search API ile AI-optimize arama yapar")
    elif hasattr(motor, "_registry") and motor._registry:
        motor._registry.kaydet("TAVILY_ARA", tavily_ara)

    logger.info("[Plugin:tavily] Tavily Search plugin kayit edildi.")
