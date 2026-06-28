"""
Supermemory bellek arka ucu.

Supermemory.ai API üzerinden bulut tabanlı bellek yönetimi.
"""

import json
import logging
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


class SupermemoryBackend:
    """Supermemory.ai API bellek arka ucu."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.supermemory.ai/v1"

    def ekle(self, icerik: str, kaynak: Optional[str] = None) -> dict[str, Any]:
        """Supermemory'e yeni bir bellek ekler.

        Args:
            icerik: Kaydedilecek içerik.
            kaynak: İçerik kaynağı (URL, dosya adı, vb.).

        Returns:
            API yanıtı.
        """
        if not self.api_key:
            return {"durum": "hata", "hata": "API anahtarı bulunamadı (SUPERMEMORY_API_KEY)"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"content": icerik}
        if kaynak:
            payload["source"] = kaynak

        try:
            r = requests.post(f"{self.base_url}/memory", json=payload, headers=headers, timeout=30)
            r.raise_for_status()
            logger.info("Supermemory eklendi: %.50s", icerik)
            return {"durum": "eklendi", "yanit": r.json()}
        except Exception as e:
            logger.error("Supermemory ekleme hatası: %s", e)
            return {"durum": "hata", "hata": str(e)}

    def ara(self, sorgu: str) -> list[dict[str, Any]]:
        """Supermemory'de arama yapar.

        Args:
            sorgu: Arama sorgusu.

        Returns:
            Eşleşen bellekler.
        """
        if not self.api_key:
            return [{"hata": "API anahtarı bulunamadı"}]

        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"q": sorgu}
        try:
            r = requests.get(f"{self.base_url}/memory/search", params=params, headers=headers, timeout=30)
            r.raise_for_status()
            return r.json().get("results", [])
        except Exception as e:
            logger.error("Supermemory arama hatası: %s", e)
            return []

    def listele(self, limit: int = 20) -> list[dict[str, Any]]:
        """Son bellekleri listeler.

        Args:
            limit: Maksimum sonuç sayısı.

        Returns:
            Bellek listesi.
        """
        if not self.api_key:
            return []

        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"limit": limit}
        try:
            r = requests.get(f"{self.base_url}/memory", params=params, headers=headers, timeout=30)
            r.raise_for_status()
            return r.json().get("memories", [])
        except Exception as e:
            logger.error("Supermemory listeleme hatası: %s", e)
            return []

    def run(self, **kwargs) -> str:
        """Arka ucu test eder."""
        if not self.api_key:
            return json.dumps({
                "durum": "api_anahtari_yok",
                "mesaj": "SUPERMEMORY_API_KEY ortam değişkeni ayarlanmamış",
            }, indent=2, ensure_ascii=False)

        test_icerik = kwargs.get("icerik", "Test bellek girdisi")
        sonuc = self.ekle(test_icerik)
        return json.dumps(sonuc, indent=2, ensure_ascii=False)
