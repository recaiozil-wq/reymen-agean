"""
Photon/iMessage eklentisi.

Photon (BlueBubbles) API üzerinden iMessage gönderme.
"""

import json
import logging
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


class PhotonPlugin:
    """Photon (BlueBubbles) iMessage eklentisi."""

    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        self.api_url = api_url or "http://localhost:8080/api/v1"
        self.api_key = api_key

    def mesaj_gonder(self, hedef: str, metin: str) -> dict[str, Any]:
        """iMessage gönderir (Photon/BlueBubbles API).

        Args:
            hedef: Telefon numarası veya e-posta.
            metin: Mesaj metni.

        Returns:
            API yanıtı.
        """
        if not self.api_key:
            return {"durum": "hata", "hata": "API anahtarı belirtilmedi"}

        headers = {"Authorization": self.api_key, "Content-Type": "application/json"}
        payload = {
            "chatGuid": hedef,
            "text": metin,
        }
        try:
            r = requests.post(f"{self.api_url}/message/text", json=payload, headers=headers, timeout=30)
            r.raise_for_status()
            logger.info("Photon mesajı gönderildi -> %s: %.50s", hedef, metin)
            return {"durum": "gonderildi", "yanit": r.json()}
        except Exception as e:
            logger.error("Photon mesaj hatası: %s", e)
            return {"durum": "hata", "hata": str(e)}

    def run(self, **kwargs) -> str:
        """Eklentiyi çalıştırır."""
        hedef = kwargs.get("hedef", "+1234567890")
        metin = kwargs.get("metin", "Test mesajı — iMessage")
        sonuc = self.mesaj_gonder(hedef, metin)
        return json.dumps(sonuc, indent=2, ensure_ascii=False)
