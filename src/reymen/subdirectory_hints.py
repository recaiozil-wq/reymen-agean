# -*- coding: utf-8 -*-
"""Alt dizin ipuclari — terminal tool icin dogru klasoru onerir.

Hermes agent/subdirectory_hints.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def proje_koku_bul() -> Path:
    """Proje kokunu bul (pyproject.toml, setup.py veya .git ara)."""
    yol = Path.cwd()
    for parent in [yol] + list(yol.parents):
        if any((parent / f).exists() for f in ["pyproject.toml", "setup.py", ".git"]):
            return parent
    return yol

def alt_klasor_oner(kelime: str) -> str:
    """Kelimeye gore alt klasor oner."""
    eslesmeler = {
        "test": "tests", "src": "src", "docs": "docs",
        "config": "config", "script": "scripts", "skill": "skills"
    }
    for k, v in eslesmeler.items():
        if k in kelime.lower():
            return v
    return ""
