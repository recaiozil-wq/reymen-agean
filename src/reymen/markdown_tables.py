# -*- coding: utf-8 -*-
"""Tablo formatlama yardimcilari.

Hermes agent/markdown_tables.py'den adapte edilmistir.
"""
from __future__ import annotations
from typing import List

def tablo_yap(basliklar: List[str], satirlar: List[List[str]]) -> str:
    """Markdown tablosu olustur."""
    if not basliklar or not satirlar:
        return ""
    kolon_sayisi = len(basliklar)
    cizgi = "|".join("---" for _ in range(kolon_sayisi))
    parcalar = ["|" + "|".join(basliklar) + "|", "|" + cizgi + "|"]
    for satir in satirlar:
        while len(satir) < kolon_sayisi:
            satir.append("")
        parcalar.append("|" + "|".join(str(s)[:60] for s in satir[:kolon_sayisi]) + "|")
    return "\n".join(parcalar)

def tablo_dene(metin: str) -> bool:
    """Metin tablo iceriyor mu?"""
    import re
    return bool(re.search(r"\|.*\|.*\|", metin))
