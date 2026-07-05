# -*- coding: utf-8 -*-
"""Provider rate limit takibi — 429/401 hatalarini izler ve fallback yoneti.

Hermes agent/rate_limit_tracker.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
import time
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class RateLimitTracker:
    """Provider rate limit takipcisi. 429/401 hatalarini sayar, fallback karari verir."""

    def __init__(self, max_hata: int = 3, reset_suresi: float = 300.0):
        self.max_hata = max_hata
        self.reset_suresi = reset_suresi
        self._hata_sayaci: Dict[str, int] = {}
        self._son_hata: Dict[str, float] = {}

    def hata_kaydet(self, provider: str, hata_kodu: int) -> None:
        """Provider hatasini kaydet."""
        simdi = time.time()
        self._son_hata[provider] = simdi
        if provider not in self._hata_sayaci:
            self._hata_sayaci[provider] = 0
        self._hata_sayaci[provider] += 1
        logger.debug("[RateLimit] %s hata %d (toplam: %d)", provider, hata_kodu, self._hata_sayaci[provider])

    def bloke_mi(self, provider: str) -> bool:
        """Provider gecici olarak bloke mi?"""
        hata_sayisi = self._hata_sayaci.get(provider, 0)
        son_hata = self._son_hata.get(provider, 0)
        if hata_sayisi >= self.max_hata:
            if time.time() - son_hata < self.reset_suresi:
                return True
            self._hata_sayaci[provider] = 0
        return False

    def kullanilabilir_providerlar(self, providers: list) -> list:
        """Bloke olmayan providerlari filtrele."""
        return [p for p in providers if not self.bloke_mi(p)]

    def sifirla(self, provider: Optional[str] = None) -> None:
        if provider:
            self._hata_sayaci.pop(provider, None)
            self._son_hata.pop(provider, None)
        else:
            self._hata_sayaci.clear()
            self._son_hata.clear()

# Singleton
_rate_limit_tracker = RateLimitTracker()

def tracker_al() -> RateLimitTracker:
    return _rate_limit_tracker
