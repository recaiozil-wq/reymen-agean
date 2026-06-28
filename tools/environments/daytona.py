"""
Daytona bulut geliştirme ortamı eklentisi.

Daytona API üzerinden bulut tabanlı geliştirme ortamları.
"""

import json
import logging
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


class DaytonaEnvironment:
    """Daytona bulut geliştirme ortamı yöneticisi."""

    def __init__(self, api_key: Optional[str] = None, api_url: str = "https://api.daytona.io/v1"):
        self.api_key = api_key
        self.api_url = api_url

    def ortam_olustur(self, isim: str, image: str = "ubuntu:22.04") -> dict[str, Any]:
        """Daytona'da yeni bir geliştirme ortamı oluşturur.

        Args:
            isim: Ortam adı.
            image: Kullanılacak Docker imajı.

        Returns:
            Oluşturulan ortam bilgisi.
        """
        if not self.api_key:
            return {"durum": "hata", "hata": "API anahtarı bulunamadı (DAYTONA_API_KEY)"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"name": isim, "image": image}
        try:
            r = requests.post(f"{self.api_url}/environments", json=payload, headers=headers, timeout=60)
            r.raise_for_status()
            logger.info("Daytona ortamı oluşturuldu: %s", isim)
            return {"durum": "olusturuldu", "ortam": r.json()}
        except Exception as e:
            logger.error("Daytona ortam oluşturma hatası: %s", e)
            return {"durum": "hata", "hata": str(e)}

    def ortam_sil(self, ortam_id: str) -> dict[str, Any]:
        """Daytona ortamını siler.

        Args:
            ortam_id: Silinecek ortam ID'si.

        Returns:
            İşlem sonucu.
        """
        if not self.api_key:
            return {"durum": "hata", "hata": "API anahtarı bulunamadı"}

        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            r = requests.delete(f"{self.api_url}/environments/{ortam_id}", headers=headers, timeout=30)
            r.raise_for_status()
            logger.info("Daytona ortamı silindi: %s", ortam_id)
            return {"durum": "silindi"}
        except Exception as e:
            logger.error("Daytona silme hatası: %s", e)
            return {"durum": "hata", "hata": str(e)}

    def ortam_listele(self) -> list[dict[str, Any]]:
        """Tüm Daytona ortamlarını listeler."""
        if not self.api_key:
            return []

        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            r = requests.get(f"{self.api_url}/environments", headers=headers, timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error("Daytona listeleme hatası: %s", e)
            return []

    def run(self, **kwargs) -> str:
        """Eklentiyi çalıştırır."""
        isim = kwargs.get("isim", "test-ortam")
        sonuc = self.ortam_olustur(isim)
        return json.dumps(sonuc, indent=2, ensure_ascii=False)
