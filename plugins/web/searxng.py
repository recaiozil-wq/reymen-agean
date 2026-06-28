"""
SearXNG arama eklentisi.

Kendi kendine barındırılan SearXNG meta arama motoru.
"""

import json
import logging
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


class SearXNGPlugin:
    """SearXNG meta arama eklentisi."""

    def __init__(self, base_url: str = "http://localhost:8888"):
        self.base_url = base_url

    def ara(self, sorgu: str, kategori: str = "general", limit: int = 10) -> list[dict[str, Any]]:
        """SearXNG üzerinde arama yapar.

        Args:
            sorgu: Arama sorgusu.
            kategori: Arama kategorisi (general, science, news, etc.).
            limit: Maksimum sonuç sayısı.

        Returns:
            Arama sonuçları listesi.
        """
        params = {
            "q": sorgu,
            "format": "json",
            "categories": kategori,
            "limit": limit,
        }
        try:
            r = requests.get(f"{self.base_url}/search", params=params, timeout=30)
            r.raise_for_status()
            veri = r.json()
            sonuclar = veri.get("results", [])
            logger.info("SearXNG araması: '%s' -> %d sonuç", sorgu, len(sonuclar))
            return sonuclar[:limit]
        except requests.ConnectionError:
            logger.warning("SearXNG bağlantı hatası: %s", self.base_url)
            return []
        except Exception as e:
            logger.error("SearXNG arama hatası: %s", e)
            return []

    def run(self, **kwargs) -> str:
        """Eklentiyi çalıştırır."""
        sorgu = kwargs.get("sorgu", "test")
        sonuclar = self.ara(sorgu)
        return json.dumps(sonuclar, indent=2, ensure_ascii=False)
