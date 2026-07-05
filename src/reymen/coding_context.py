# -*- coding: utf-8 -*-
"""Kodlama gorevleri icin context olusturma.

Hermes agent/coding_context.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

def kod_context_al(proje_yolu: Optional[Path] = None) -> str:
    """Projedeki kod dosyalarinin listesini ve yapisini dondur."""
    try:
        kok = proje_yolu or Path.cwd()
        parcalar = [f"Proje: {kok.name}"]
        for py in sorted(kok.rglob("*.py")):
            if ".venv" in str(py) or "__pycache__" in str(py):
                continue
            parcalar.append(f"  {py.relative_to(kok)}")
        return "\n".join(parcalar[:30])
    except Exception as e:
        logger.debug("Kod context hatasi: %s", e)
        return ""
