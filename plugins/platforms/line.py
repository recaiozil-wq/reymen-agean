"""
LINE mesajlaşma eklentisi.

LINE Messaging API üzerinden mesaj gönderme.
"""

import json
import logging
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


class LINEPlugin:
    """LINE Messaging API eklentisi."""

    def __init__(self, channel_token: Optional[str] = None):
        self.channel_token = channel_token
        self.base_url = "https://api.line.me/v2/bot"

    def mesaj_gonder(self, hedef: str, metin: str) -> dict[str, Any]:
        """LINE kullanıcısına mesaj gönderir.

        Args:
            hedef: Alıcı kullanıcı ID'si.
            metin: Mesaj metni.

        Returns:
            API yanıtı.
        """
        if not self.channel_token:
            return {"durum": "hata", "hata": "Channel token belirtilmedi"}

        headers = {
            "Authorization": f"Bearer {self.channel_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "to": hedef,
            "messages": [{"type": "text", "text": metin}],
        }
        try:
            r = requests.post(f"{self.base_url}/message/push", json=payload, headers=headers, timeout=30)
            r.raise_for_status()
            logger.info("LINE mesajı gönderildi -> %s: %.50s", hedef, metin)
            return {"durum": "gonderildi", "yanit": r.status_code}
        except Exception as e:
            logger.error("LINE mesaj hatası: %s", e)
            return {"durum": "hata", "hata": str(e)}

    def run(self, **kwargs) -> str:
        """Eklentiyi çalıştırır."""
        hedef = kwargs.get("hedef", "test_user")
        metin = kwargs.get("metin", "Test mesajı — LINE")
        sonuc = self.mesaj_gonder(hedef, metin)
        return json.dumps(sonuc, indent=2, ensure_ascii=False)
