"""
DuckDuckGo arama eklentisi.

DuckDuckGo üzerinden web araması (API gerektirmez).
"""

import json
import logging
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


class DDGSPlugin:
    """DuckDuckGo arama eklentisi (API anahtarı gerekmez)."""

    def __init__(self):
        self.base_url = "https://api.duckduckgo.com"

    def ara(self, sorgu: str) -> list[dict[str, Any]]:
        """DuckDuckGo Instant Answer API ile arama yapar.

        Args:
            sorgu: Arama sorgusu.

        Returns:
            Sonuçlar listesi.
        """
        params = {
            "q": sorgu,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1,
        }
        try:
            r = requests.get(f"{self.base_url}", params=params, timeout=15)
            r.raise_for_status()
            veri = r.json()
            sonuclar = []

            # Abstract text
            if veri.get("AbstractText"):
                sonuclar.append({
                    "baslik": veri.get("Heading", ""),
                    "ozet": veri.get("AbstractText", ""),
                    "kaynak": veri.get("AbstractSource", ""),
                    "url": veri.get("AbstractURL", ""),
                })

            # Related topics
            for topic in veri.get("RelatedTopics", []):
                if "Text" in topic:
                    sonuclar.append({
                        "baslik": topic.get("Text", ""),
                        "ozet": topic.get("FirstURL", ""),
                        "url": topic.get("FirstURL", ""),
                    })

            logger.info("DDGS araması: '%s' -> %d sonuç", sorgu, len(sonuclar))
            return sonuclar
        except Exception as e:
            logger.error("DDGS arama hatası: %s", e)
            return []

    def run(self, **kwargs) -> str:
        """Eklentiyi çalıştırır."""
        sorgu = kwargs.get("sorgu", "test")
        sonuclar = self.ara(sorgu)
        return json.dumps(sonuclar, indent=2, ensure_ascii=False)
