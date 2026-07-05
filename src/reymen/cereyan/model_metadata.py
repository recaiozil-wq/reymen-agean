# -*- coding: utf-8 -*-
"""Model metadata — provider/model bilgilerini tutar.

Hermes agent/model_metadata.py'den adapte edilmistir.
"""
from __future__ import annotations
from typing import Dict, Optional

MODEL_BILGISI: Dict[str, dict] = {
    "deepseek-v4-flash": {"provider": "deepseek", "context": 65536, "tur": "chat"},
    "mimo-v2.5-pro": {"provider": "xiaomi", "context": 32768, "tur": "chat"},
    "lmstudio": {"provider": "local", "context": 8192, "tur": "chat"},
}

def model_bilgisi_al(model: str) -> Optional[dict]:
    return MODEL_BILGISI.get(model)

def context_boyutu(model: str) -> int:
    info = MODEL_BILGISI.get(model, {})
    return info.get("context", 8192)
