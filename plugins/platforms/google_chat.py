"""
Google Chat webhook eklentisi.

Google Chat webhook URL'leri üzerinden mesaj gönderme.
"""

import json
import logging
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


class GoogleChatPlugin:
    """Google Chat webhook mesajlaşma eklentisi."""

    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url

    def mesaj_gonder(self, metin: str, baslik: Optional[str] = None) -> dict[str, Any]:
        """Google Chat webhook'a mesaj gönderir.

        Args:
            metin: Gönderilecek mesaj metni.
            baslik: İsteğe bağlı kart başlığı.

        Returns:
            API yanıtı.
        """
        if not self.webhook_url:
            return {"durum": "hata", "hata": "Webhook URL belirtilmedi"}

        if baslik:
            payload = {
                "cards": [{
                    "header": {"title": baslik},
                    "sections": [{"text": metin}],
                }]
            }
        else:
            payload = {"text": metin}

        try:
            r = requests.post(self.webhook_url, json=payload, timeout=30)
            r.raise_for_status()
            logger.info("Google Chat mesajı gönderildi: %.50s", metin)
            return {"durum": "gonderildi", "yanit": r.status_code}
        except Exception as e:
            logger.error("Google Chat mesaj hatası: %s", e)
            return {"durum": "hata", "hata": str(e)}

    def run(self, **kwargs) -> str:
        """Eklentiyi çalıştırır/test eder."""
        metin = kwargs.get("metin", "Test mesajı — Google Chat")
        sonuc = self.mesaj_gonder(metin)
        return json.dumps(sonuc, indent=2, ensure_ascii=False)
