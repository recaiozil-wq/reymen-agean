# -*- coding: utf-8 -*-
"""Ilk kullanim yonlendirme — yeni kullaniciya rehberlik eder.

Hermes agent/onboarding.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class Onboarding:
    """Ilk kullanim deneyimi yoneticisi."""

    def __init__(self, durum_yolu: Optional[Path] = None):
        self.durum_yolu = durum_yolu or Path.cwd() / ".ReYMeN" / "onboarding.json"
        self.durum_yolu.parent.mkdir(parents=True, exist_ok=True)

    def tamamlandi_mi(self) -> bool:
        return self.durum_yolu.exists()

    def tamamla(self) -> None:
        import json, datetime
        self.durum_yolu.write_text(json.dumps({"tarih": datetime.datetime.now().isoformat()}), encoding="utf-8")

    def adim_mesaji(self, adim: int) -> str:
        mesajlar = [
            "ReYMeN Agent'e hos geldin! 'merhaba' yazarak baslayabilirsin.",
            "Bana bir hedef ver, ben araclari kullanarak cozeyim.",
            "Istersen /yardim yazarak tum komutlari gorebilirsin."
        ]
        return mesajlar[adim] if adim < len(mesajlar) else ""
