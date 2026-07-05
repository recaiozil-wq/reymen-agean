# -*- coding: utf-8 -*-
"""Skill paketleme — birden cok skill'i tek dosyada birlestirir.

Hermes agent/skill_bundles.py'den adapte edilmistir.
"""
from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class SkillBundle:
    """Birden cok skill'i tek bir bundle'da topla."""

    def __init__(self, bundle_path: Optional[Path] = None):
        self.bundle_path = bundle_path or Path.cwd() / ".ReYMeN" / "skill_bundles"
        self.bundle_path.mkdir(parents=True, exist_ok=True)

    def bundle_skills(self, skill_names: List[str], bundle_name: str) -> str:
        """Skill'leri bundle yap."""
        data = {"bundle_name": bundle_name, "skills": skill_names, "version": 1}
        path = self.bundle_path / f"{bundle_name}.bundle.json"
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return str(path)

    def list_bundles(self) -> List[str]:
        if not self.bundle_path.exists():
            return []
        return [f.stem for f in self.bundle_path.glob("*.bundle.json")]

    def load_bundle(self, bundle_name: str) -> Optional[Dict]:
        path = self.bundle_path / f"{bundle_name}.bundle.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return None
