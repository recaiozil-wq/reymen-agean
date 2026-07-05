# -*- coding: utf-8 -*-
"""Agent yorungesi — adim adim ne yapildigini kaydeder.

Hermes agent/trajectory.py'den adapte edilmistir.
"""
from __future__ import annotations
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class Trajectory:
    """Agent adimlarini kaydeder."""

    def __init__(self, kayit_yolu: Optional[Path] = None):
        self.kayit_yolu = kayit_yolu or Path.cwd() / ".ReYMeN" / "trajectory.jsonl"
        self.kayit_yolu.parent.mkdir(parents=True, exist_ok=True)
        self._adimlar: List[Dict] = []

    def adim_ekle(self, tur: str, detay: str, basarili: bool = True) -> None:
        kayit = {"zaman": datetime.now().isoformat(), "tur": tur, "detay": detay[:200], "basarili": basarili}
        self._adimlar.append(kayit)
        try:
            with open(self.kayit_yolu, "a", encoding="utf-8") as f:
                f.write(json.dumps(kayit, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.debug("Trajectory kayit hatasi: %s", e)

    def son_adimlar(self, n: int = 5) -> List[Dict]:
        return self._adimlar[-n:]
