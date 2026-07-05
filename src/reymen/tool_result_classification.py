# -*- coding: utf-8 -*-
"""Tool sonuclarini siniflandirma.

Hermes agent/tool_result_classification.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

def siniflandir(sonuc: Dict) -> str:
    """Tool sonucunu siniflandir: basarili, hata, uyari, bos."""
    if sonuc.get("basarili"):
        cikti = str(sonuc.get("cikti", ""))
        if not cikti.strip():
            return "bos"
        if len(cikti) > 1000:
            return "buyuk_cikti"
        return "basarili"
    return "hata" if sonuc.get("hata") else "basarisiz"
