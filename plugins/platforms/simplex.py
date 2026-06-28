"""
SimpleX gizlilik eklentisi.

SimpleX privacy platformu üzerinden mesajlaşma.
"""

import json
import logging
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


class SimpleXPlugin:
    """SimpleX mesajlaşma eklentisi (SMTP bazlı)."""

    def __init__(self, smp_server: Optional[str] = None):
        self.smp_server = smp_server or "smp.simplex.im"

    def mesaj_gonder(self, hedef_adres: str, metin: str) -> dict[str, Any]:
        """SimpleX üzerinden mesaj gönderir (API üzerinden).

        Args:
            hedef_adres: Hedef SimpleX adresi.
            metin: Mesaj metni.

        Returns:
            İşlem sonucu.
        """
        # SimpleX henüz genel REST API sunmuyor — CLI bazlı
        try:
            import subprocess
            sonuc = subprocess.run(
                ["simplex", "chat", "--send", hedef_adres, metin],
                capture_output=True, text=True, timeout=30,
            )
            if sonuc.returncode == 0:
                logger.info("SimpleX mesajı gönderildi -> %s", hedef_adres)
                return {"durum": "gonderildi", "cikti": sonuc.stdout}
            else:
                return {"durum": "hata", "hata": sonuc.stderr}
        except FileNotFoundError:
            return {"durum": "hata", "hata": "SimpleX CLI bulunamadı (simplex chat)"}
        except Exception as e:
            logger.error("SimpleX mesaj hatası: %s", e)
            return {"durum": "hata", "hata": str(e)}

    def run(self, **kwargs) -> str:
        """Eklentiyi çalıştırır."""
        hedef = kwargs.get("hedef", "")
        metin = kwargs.get("metin", "Test mesajı — SimpleX")
        sonuc = self.mesaj_gonder(hedef, metin)
        return json.dumps(sonuc, indent=2, ensure_ascii=False)
