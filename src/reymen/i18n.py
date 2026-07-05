# -*- coding: utf-8 -*-
"""Uluslararasi lastirma (i18n) - Turkce destek.

Hermes agent/i18n.py'den adapte.
"""
from __future__ import annotations

MESAJLAR = {
    "hosgeldin": "ReYMeN Agent'e hos geldin!",
    "yardim": "Yardim icin /yardim yazin.",
    "hata": "Bir hata olustu.",
}

def mesaj_al(anahtar: str) -> str:
    return MESAJLAR.get(anahtar, anahtar)
