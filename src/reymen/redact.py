# -*- coding: utf-8 -*-
"""Veri gizleme — API key'leri ve hassas verileri maskele.

Hermes agent/redact.py'den adapte.
"""
from __future__ import annotations
import re

def redakte_et(metin: str) -> str:
    """API key, token ve sifreleri maskele."""
    metin = re.sub(r"(api[_-]?key|token|password|secret)\s*[:=]\s*\S+", r"\1: ***", metin, flags=re.IGNORECASE)
    metin = re.sub(r"(sk-[a-zA-Z0-9]{10,})", "sk-***", metin)
    metin = re.sub(r"(ghp_[a-zA-Z0-9]{10,})", "ghp_***", metin)
    return metin
