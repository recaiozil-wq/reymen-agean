# -*- coding: utf-8 -*-
"""Skill on-isleme — skill belgelerini temizle ve dogrula.

Hermes agent/skill_preprocessing.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
import re
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

def skill_dogrula(skill_path: Path) -> bool:
    """Skill dosyasini dogrula."""
    if not skill_path.exists():
        return False
    try:
        icerik = skill_path.read_text(encoding="utf-8")
        if not icerik.strip():
            return False
        if skill_path.suffix == ".md":
            return bool(re.match(r"^#\s", icerik) or "---" in icerik[:100])
        return True
    except Exception:
        return False

def skill_frontmatter_oku(skill_path: Path) -> Optional[dict]:
    """YAML frontmatter'i oku."""
    try:
        icerik = skill_path.read_text(encoding="utf-8")
        if icerik.startswith("---"):
            import yaml
            import re as _re
            match = _re.search(r"^---\s*\n(.*?)\n---", icerik, _re.DOTALL)
            if match:
                return yaml.safe_load(match.group(1))
        return None
    except Exception:
        return None
