# -*- coding: utf-8 -*-
"""Tool cagrilari icin yardimci fonksiyonlar.

Hermes agent/tool_dispatch_helpers.py'den adapte edilmistir.
"""
from __future__ import annotations
import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

def tool_args_coz(argumanlar: Any) -> Dict:
    """Tool argumanlarini JSON dict'e cevir."""
    if isinstance(argumanlar, dict):
        return argumanlar
    if isinstance(argumanlar, str):
        try:
            return json.loads(argumanlar)
        except json.JSONDecodeError:
            return {"input": argumanlar}
    return {}

def tool_sonuc_hazirla(basarili: bool, cikti: Any = "", hata: str = "") -> Dict:
    return {"basarili": basarili, "cikti": str(cikti), "hata": hata, "tamamlandi": basarili}

def is_destructive_command(komut: str) -> bool:
    """Zararli komutlari tespit et."""
    tehlikeli = ["rm -rf", "del /f", "format", "dd if=", "> /dev/sda", ":(){ :|:& };:"]
    return any(t in komut.lower() for t in tehlikeli)
