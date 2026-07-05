# -*- coding: utf-8 -*-
"""Jiter JSON parser on-yukleme.

Hermes agent/jiter_preload.py'den adapte edilmistir.
"""
from __future__ import annotations

def json_parse(metin: str) -> dict:
    """JSON parse et, hata olursa bos dict don."""
    import json
    try:
        return json.loads(metin)
    except json.JSONDecodeError:
        return {}
