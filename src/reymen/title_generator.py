# -*- coding: utf-8 -*-
"""Konusma basligi olusturucu.

Hermes agent/title_generator.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

def baslik_olustur(mesajlar: List[dict], maks_uzunluk: int = 60) -> str:
    """Ilk kullanici mesajindan konusma basligi cikar."""
    try:
        for m in mesajlar:
            if m.get("role") == "user":
                icerik = str(m.get("content", ""))[:maks_uzunluk]
                if icerik:
                    return icerik.strip() + ("..." if len(str(m.get("content",""))) > maks_uzunluk else "")
        return "Bos konusma"
    except Exception as e:
        logger.debug("Baslik olusturma hatasi: %s", e)
        return "Konusma"
