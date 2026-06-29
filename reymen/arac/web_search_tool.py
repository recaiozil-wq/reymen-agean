# -*- coding: utf-8 -*-
"""web_search_tool.py — WEB_ARA tool implementasyonu.

DuckDuckGo uzerinden arama yapar. API key gerektirmez.
Oncelik: duckduckgo-search kutuphanesi (pip install duckduckgo-search)
Fallback: DDG lite HTML scraping

Kullanim:
    from reymen.arac.web_search_tool import web_ara, web_arama_kaydet
    sonuc = web_ara("dolar kuru")
"""

import json
import logging
import re
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from typing import Optional

log = logging.getLogger(__name__)

# Basit sonuc cache: ayni sorgu 30sn icinde tekrarlanirsa cache'den
_sonuc_cache: dict[str, tuple[float, str]] = {}
_CACHE_TTL = 30  # saniye


class _DDGLiteParser(HTMLParser):
    """DDG lite HTML sayfasindan arama sonuclarini ayristirir."""

    def __init__(self) -> None:
        super().__init__()
        self.results: list[dict] = []
        self._current: Optional[dict] = None
        self._in_link = False
        self._skip_domains = {"duckduckgo.com", "wikipedia.org"}

    def handle_starttag(self, tag: str, attrs: list) -> None:
        attrs_d = dict(attrs)
        if tag == "a" and "href" in attrs_d:
            href = attrs_d["href"]
            if href.startswith("http") and not any(
                d in href for d in self._skip_domains
            ):
                self._in_link = True
                self._current = {"href": href, "title": "", "body": ""}

    def handle_data(self, data: str) -> None:
        if self._in_link and self._current is not None:
            self._current["title"] += data.strip()

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._current is not None and self._current.get("title", "").strip():
            self.results.append(self._current)
            self._current = None
            self._in_link = False


def _ddg_lite_ara(sorgu: str, max_sonuc: int = 5) -> list[dict]:
    """DDG lite HTML uzerinden arama. API key gerekmez."""
    url = "https://lite.duckduckgo.com/lite/"
    data = urllib.parse.urlencode({"q": sorgu}).encode()
    req = urllib.request.Request(url, data=data)
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    req.add_header("Accept", "text/html")

    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode("utf-8", errors="replace")

    parser = _DDGLiteParser()
    parser.feed(html)

    return parser.results[:max_sonuc]


def _ddgs_library_ara(sorgu: str, max_sonuc: int = 5) -> Optional[list[dict]]:
    """duckduckgo-search kutuphanesi ile ara (oncelikli)."""
    try:
        from duckduckgo_search import DDGS

        ddgs = DDGS()
        results = list(ddgs.text(sorgu, max_results=max_sonuc))
        # ddgs'in context manager'i yoksa manual cleanup
        if hasattr(ddgs, "close"):
            ddgs.close()
        if results:
            return [
                {
                    "href": r.get("href", ""),
                    "title": r.get("title", ""),
                    "body": r.get("body", ""),
                }
                for r in results
            ]
    except Exception as e:
        log.debug("duckduckgo-search kutuphanesi calismadi: %s", e)
    return None


def web_ara(sorgu: str, max_sonuc: int = 5) -> str:
    """Dis dunyada arama yap. API key gerekmez.

    Args:
        sorgu: Arama sorgusu.
        max_sonuc: Maks sonuc sayisi.

    Returns:
        String: "[1] Baslik | url | ozet" formatinda sonuclar
        veya "Sonuc bulunamadi." mesaji.
    """
    # Cache kontrol
    simdi = time.time()
    cache_key = sorgu.strip().lower()
    if cache_key in _sonuc_cache:
        zaman, sonuc = _sonuc_cache[cache_key]
        if simdi - zaman < _CACHE_TTL:
            log.debug("WEB_ARA cache hit: %.30s", sorgu)
            return sonuc

    # 1. duckduckgo-search kutuphanesi (oncelikli)
    results = _ddgs_library_ara(sorgu, max_sonuc)

    # 2. Fallback: DDG lite HTML
    if results is None:
        results = _ddg_lite_ara(sorgu, max_sonuc)

    if not results:
        return "Sonuc bulunamadi."

    satirlar = []
    for i, r in enumerate(results, 1):
        title = (r.get("title") or "").strip()
        href = (r.get("href") or "").strip()
        body = (r.get("body") or "").strip()
        if body:
            body = body[:200]
        satirlar.append(f"[{i}] {title}")
        if href:
            satirlar.append(f"     {href}")
        if body:
            satirlar.append(f"     {body}")

    sonuc_metin = "\n".join(satirlar)

    # Cache'e kaydet
    _sonuc_cache[cache_key] = (simdi, sonuc_metin)

    return sonuc_metin


def web_arama_kaydet(motor) -> None:
    """WEB_ARA tool'unu motor'a kaydet.

    Cagri:
        motor._plugin_arac_kaydet("WEB_ARA", web_ara, "Web'de ara")
    """
    motor._plugin_arac_kaydet("WEB_ARA", web_ara, "Web aramasi yapar (DuckDuckGo, API key gerekmez)")


def motor_kaydet(motor) -> None:
    """Motor tarafindan otomatik cagrilir. WEB_ARA tool'unu kaydeder."""
    web_arama_kaydet(motor)


if __name__ == "__main__":
    # Test
    import sys
    sonuc = web_ara(" ".join(sys.argv[1:]) if len(sys.argv) > 1 else "test")
    print(sonuc)
