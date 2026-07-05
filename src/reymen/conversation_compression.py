# -*- coding: utf-8 -*-
"""Uzun konusmalari ozetleme — context budget icin.

Hermes agent/conversation_compression.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

def konusma_ozetle(mesajlar: List[Dict], maks_mesaj: int = 20) -> List[Dict]:
    """Uzun konusmayi kisa ozete cevir. Eski mesajlari tek bir ozet mesaja donusturur."""
    if len(mesajlar) <= maks_mesaj + 1:
        return mesajlar

    # Ilk mesajlari al (sistem prompt + ilk kullanici mesaji)
    korunacak = mesajlar[:3]
    # Son mesajlari al (guncel konusma)
    korunacak += mesajlar[-(maks_mesaj - 3):]

    # Ozet olustur
    ozet_metin = f"[KONUSMA OZETI - {len(mesajlar)} mesaj {len(mesajlar)-maks_mesaj} mesaj silindi]"
    korunacak.insert(3, {"role": "system", "content": ozet_metin})
    return korunacak

def mesaj_boyutu(mesajlar: List[Dict]) -> int:
    """Mesaj listesinin toplam karakter sayisi."""
    return sum(len(str(m.get("content", ""))) for m in mesajlar)

def cok_uzun_mu(mesajlar: List[Dict], sinir: int = 300000) -> bool:
    return mesaj_boyutu(mesajlar) > sinir
