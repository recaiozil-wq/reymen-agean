# -*- coding: utf-8 -*-
"""gateway/pairing.py — Cihaz Eslestirme.

Gateway'e baglanan cihazlari eslestirme ve dogrulama.
"""

import hashlib
import os
import time
import threading
from pathlib import Path

PAIRING_DB = Path(__file__).parent.parent / ".ReYMeN" / "pairing.json"


class PairingManager:
    def __init__(self):
        self._cihazlar: dict[str, dict] = {}
        self._kilit = threading.Lock()
        self._yukle()

    def _yukle(self):
        if PAIRING_DB.exists():
            import json
            try:
                self._cihazlar = json.loads(PAIRING_DB.read_text(encoding="utf-8"))
            except Exception:
                self._cihazlar = {}

    def _kaydet(self):
        import json
        PAIRING_DB.parent.mkdir(parents=True, exist_ok=True)
        PAIRING_DB.write_text(
            json.dumps(self._cihazlar, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def eslestirme_kodu_uret(self) -> str:
        """6 haneli eslestirme kodu uret."""
        import random
        return str(random.randint(100000, 999999))

    def eslestir(self, cihaz_adi: str, platform: str) -> dict:
        """Yeni bir cihazi eslestir.

        Args:
            cihaz_adi: Cihaz adi
            platform: Platform turu

        Returns:
            Eslestirme bilgileri (kod, token)
        """
        import uuid
        kod = self.eslestirme_kodu_uret()
        token = uuid.uuid4().hex[:32]

        with self._kilit:
            self._cihazlar[token] = {
                "cihaz_adi": cihaz_adi,
                "platform": platform,
                "kod": kod,
                "zaman": time.time(),
                "dogrulandi": False,
            }
            self._kaydet()

        return {"kod": kod, "token": token}

    def dogrula(self, kod: str) -> str:
        """Kod ile eslestirmeyi dogrula.

        Args:
            kod: Eslestirme kodu

        Returns:
            Token veya bos string
        """
        with self._kilit:
            for token, bilgi in self._cihazlar.items():
                if bilgi.get("kod") == kod and not bilgi.get("dogrulandi"):
                    bilgi["dogrulandi"] = True
                    self._kaydet()
                    return token
        return ""

    def liste(self) -> list[dict]:
        with self._kilit:
            return [
                {"cihaz": c["cihaz_adi"], "platform": c["platform"], "dogrulandi": c["dogrulandi"]}
                for c in self._cihazlar.values()
            ]


# Global instance
eslestirici = PairingManager()
