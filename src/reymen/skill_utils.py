# -*- coding: utf-8 -*-
"""Skill yardimci fonksiyonlari.

Hermes agent/skill_utils.py'den adapte.
"""
from __future__ import annotations
import logging
from pathlib import Path
from typing import List
logger = logging.getLogger(__name__)

def skill_bul(klasor: Path, query: str) -> List[Path]:
    """Skill klasorunde query'ye gore ara."""
    if not klasor.exists():
        return []
    return [f for f in klasor.rglob("*.md") if query.lower() in f.read_text(encoding="utf-8", errors="replace").lower()]

def skill_sayisi(klasor: Path) -> int:
    if not klasor.exists():
        return 0
    return sum(1 for f in klasor.rglob("*.md") if f.name != "README.md")
