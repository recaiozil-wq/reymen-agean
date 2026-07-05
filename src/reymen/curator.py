# -*- coding: utf-8 -*-
"""Skill otomatik bakim — skill recog, konsolidasyon, temizlik.

Hermes agent/curator.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
import shutil
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

class SkillCurator:
    """Skill havuzu bakimini otomatik yapar."""

    def __init__(self, skill_yolu: Optional[Path] = None):
        self.skill_yolu = skill_yolu or Path.cwd() / "reymen" / "cereyan" / "skills"
        self.skill_yolu.mkdir(parents=True, exist_ok=True)

    def skill_sayisi(self) -> int:
        if not self.skill_yolu.exists():
            return 0
        return sum(1 for f in self.skill_yolu.rglob("*.md") if f.name != "README.md")

    def temizle(self, gun_siniri: int = 90) -> int:
        """Eski/bos skill dosyalarini temizle."""
        silinen = 0
        for f in self.skill_yolu.rglob("*.md"):
            if f.name == "README.md":
                continue
            try:
                icerik = f.read_text(encoding="utf-8")
                if len(icerik.strip()) < 20:
                    f.unlink()
                    silinen += 1
            except Exception:
                continue
        return silinen

    def skill_listesi(self) -> List[str]:
        if not self.skill_yolu.exists():
            return []
        return sorted(f.stem for f in self.skill_yolu.rglob("*.md") if f.name != "README.md")
