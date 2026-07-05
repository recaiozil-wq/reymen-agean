# -*- coding: utf-8 -*-
"""Context budget yonetimi — asiri uzun mesajlari sikistirir.

Hermes agent/context_compressor.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

def context_sikistir(mesajlar: List[Dict], hedef_boyut: int = 300000) -> List[Dict]:
    """Context boyutunu hedef boyutun altina indir."""
    toplam = sum(len(str(m.get("content", ""))) for m in mesajlar)
    if toplam <= hedef_boyut:
        return mesajlar

    # En eski mesajlardan baslayarak kucult
    for i in range(1, len(mesajlar) - 3):
        if toplam <= hedef_boyut:
            break
        m = mesajlar[i]
        icerik = str(m.get("content", ""))
        if len(icerik) > 200:
            yeni = icerik[:100] + "... [TRUNCATED] ..." + icerik[-50:]
            toplam -= len(icerik) - len(yeni)
            mesajlar[i]["content"] = yeni
    return mesajlar

def budget_asildi(mesajlar: List[Dict], sinir: int = 300000) -> bool:
    return sum(len(str(m.get("content", ""))) for m in mesajlar) > sinir
