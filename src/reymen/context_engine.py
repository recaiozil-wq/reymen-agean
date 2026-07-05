# -*- coding: utf-8 -*-
"""Akilli context yonetimi — onemli bilgileri onceliklendirir.

Hermes agent/context_engine.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class ContextEngine:
    """Context yonetim motoru. Onem sirasina gore context parcaciklarini secer."""

    def __init__(self, max_token: int = 4000):
        self.max_token = max_token
        self._kaynaklar: List[Dict] = []

    def ekle(self, kategori: str, icerik: str, onem: int = 5) -> None:
        self._kaynaklar.append({"kategori": kategori, "icerik": icerik, "onem": onem})

    def build(self, hedef: str = "") -> str:
        """Onem sirasina gore context build et."""
        sirali = sorted(self._kaynaklar, key=lambda x: -x["onem"])
        parcalar = []
        toplam = 0
        for k in sirali:
            if toplam >= self.max_token:
                break
            parcalar.append(k["icerik"])
            toplam += len(k["icerik"])
        return "\n\n".join(parcalar)

    def temizle(self) -> None:
        self._kaynaklar.clear()
