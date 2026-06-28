"""
Firecrawl web arama eklentisi.

Firecrawl API ile web sayfası tarama ve içerik çıkarma.
"""

import json
import logging
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


class FirecrawlPlugin:
    """Firecrawl web tarama eklentisi."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.firecrawl.dev/v1"

    def scrape(self, url: str) -> dict[str, Any]:
        """Bir URL'yi tarar ve içeriğini çıkarır.

        Args:
            url: Taranacak URL.

        Returns:
            Sayfa içeriği.
        """
        if not self.api_key:
            return {"durum": "hata", "hata": "API anahtarı bulunamadı (FIRECRAWL_API_KEY)"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"url": url}
        try:
            r = requests.post(f"{self.base_url}/scrape", json=payload, headers=headers, timeout=60)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error("Firecrawl tarama hatası (%s): %s", url, e)
            return {"durum": "hata", "hata": str(e)}

    def search(self, sorgu: str) -> dict[str, Any]:
        """Web araması yapar.

        Args:
            sorgu: Arama sorgusu.

        Returns:
            Arama sonuçları.
        """
        if not self.api_key:
            return {"durum": "hata", "hata": "API anahtarı bulunamadı"}

        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"query": sorgu}
        try:
            r = requests.get(f"{self.base_url}/search", params=params, headers=headers, timeout=60)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error("Firecrawl arama hatası (%s): %s", sorgu, e)
            return {"durum": "hata", "hata": str(e)}

    def run(self, **kwargs) -> str:
        """Eklentiyi çalıştırır."""
        url = kwargs.get("url", "https://example.com")
        sonuc = self.scrape(url)
        return json.dumps(sonuc, indent=2, ensure_ascii=False)
