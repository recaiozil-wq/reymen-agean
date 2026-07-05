# -*- coding: utf-8 -*-
"""Skill yedekleme — skill havuzunu zip ile yedekler.

Hermes agent/curator_backup.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class SkillBackup:
    """Skill havuzunu yedekler."""

    def __init__(self, kaynak: Optional[Path] = None, hedef: Optional[Path] = None):
        self.kaynak = kaynak or Path.cwd() / "reymen" / "cereyan" / "skills"
        self.hedef = hedef or Path.cwd() / ".ReYMeN" / "skill_yedek"

    def yedekle(self) -> Optional[Path]:
        if not self.kaynak.exists():
            return None
        self.hedef.mkdir(parents=True, exist_ok=True)
        zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
        arsiv = self.hedef / f"skills_{zaman}.zip"
        shutil.make_archive(str(arsiv.with_suffix("")), "zip", self.kaynak)
        logger.info("Skill yedegi olusturuldu: %s", arsiv)
        return arsiv

    def temizle(self, gun: int = 30) -> int:
        """Eski yedekleri temizle."""
        silinen = 0
        from datetime import datetime, timedelta
        sinir = datetime.now() - timedelta(days=gun)
        for f in self.hedef.glob("*.zip"):
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if mtime < sinir:
                    f.unlink()
                    silinen += 1
            except Exception:
                continue
        return silinen
