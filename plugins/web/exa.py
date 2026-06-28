"""
Exa arama eklentisi.

Exa (eski adıyla Metaphor) API üzerinden sinirsel web arama.
"""

import json
import logging
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


class ExaPlugin:
    """Exa sinirsel arama eklentisi."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.exa.ai"

    def ara(self, sorgu: str, limit: int = 10, include_domains: Optional[list[str]] = None) -> list[dict[str, Any]]:
        """Exa ile sinirsel arama yapar.

        Args:
            sorgu: Arama sorgusu.
            limit: Maksimum sonuç sayısı.
            include_domains: Sadece bu domainlerde ara.

        Returns:
            Arama sonuçları.
        """
        if not self.api_key:
            return [{"hata": "API anahtarı bulunamadı (EXA_API_KEY)"}]

        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "query": sorgu,
            "numResults": limit,
        }
        if include_domains:
            payload["includeDomains"] = include_domains

        try:
            r = requests.post(f"{self.base_url}/search", json=payload, headers=headers, timeout=30)
            r.raise_for_status()
            veri = r.json()
            sonuclar = veri.get("results", [])
            logger.info("Exa araması: '%s' -> %d sonuç", sorgu, len(sonuclar))
            return sonuclar
        except Exception as e:
            logger.error("Exa arama hatası: %s", e)
            return [{"hata": str(e)}]

    def icerik_getir(self, url: str) -> Optional[str]:
        """Exa ile bir URL'nin içeriğini getirir.

        Args:
            url: İçerik alınacak URL.

        Returns:
            Sayfa içeriği (metin).
        """
        if not self.api_key:
            return None

        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {"url": url, "text": True}
        try:
            r = requests.post(f"{self.base_url}/contents", json=payload, headers=headers, timeout=30)
            r.raise_for_status()
            veri = r.json()
            return veri.get("text")
        except Exception as e:
            logger.error("Exa içerik hatası (%s): %s", url, e)
            return None

    def run(self, **kwargs) -> str:
        """Eklentiyi çalıştırır."""
        sorgu = kwargs.get("sorgu", "test query")
        sonuclar = self.ara(sorgu)
        return json.dumps(sonuclar, indent=2, ensure_ascii=False)
