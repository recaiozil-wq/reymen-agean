# -*- coding: utf-8 -*-
"""Portal tag yonetimi.

Hermes agent/portal_tags.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

class PortalTags:
    def __init__(self):
        self._taglar = {}
    def ekle(self, anahtar: str, deger: str) -> None:
        self._taglar[anahtar] = deger
    def al(self, anahtar: str) -> str:
        return self._taglar.get(anahtar, "")
