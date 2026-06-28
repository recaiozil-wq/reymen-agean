"""
Microsoft Teams eklentisi.

Teams webhook'u üzerinden mesaj gönderme.
"""

import json
import logging
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


class TeamsPlugin:
    """Microsoft Teams webhook eklentisi."""

    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url

    def mesaj_gonder(self, metin: str, baslik: Optional[str] = None) -> dict[str, Any]:
        """Teams kanalına mesaj gönderir (Adaptive Card formatı).

        Args:
            metin: Mesaj metni.
            baslik: İsteğe bağlı kart başlığı.

        Returns:
            API yanıtı.
        """
        if not self.webhook_url:
            return {"durum": "hata", "hata": "Webhook URL belirtilmedi"}

        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "summary": baslik or "ReYMeN Mesajı",
            "themeColor": "0072C6",
            "sections": [{
                "activityTitle": baslik or "ReYMeN Bildirimi",
                "text": metin,
                "markdown": True,
            }],
        }

        try:
            r = requests.post(self.webhook_url, json=payload, timeout=30)
            r.raise_for_status()
            logger.info("Teams mesajı gönderildi: %.50s", metin)
            return {"durum": "gonderildi", "yanit": r.status_code}
        except Exception as e:
            logger.error("Teams mesaj hatası: %s", e)
            return {"durum": "hata", "hata": str(e)}

    def run(self, **kwargs) -> str:
        """Eklentiyi çalıştırır."""
        metin = kwargs.get("metin", "Test mesajı — Teams")
        baslik = kwargs.get("baslik", "ReYMeN Test")
        sonuc = self.mesaj_gonder(metin, baslik)
        return json.dumps(sonuc, indent=2, ensure_ascii=False)
