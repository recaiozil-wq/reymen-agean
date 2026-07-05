# -*- coding: utf-8 -*-
"""Skill komutlari — skill yonetimi icin CLI komutlari.

Hermes agent/skill_commands.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
from typing import List, Optional
from reymen.cereyan.skill_activator import SkillActivator

logger = logging.getLogger(__name__)
_activator = SkillActivator()

def skill_list(kategori: Optional[str] = None) -> List[str]:
    """Skill'leri listele."""
    try:
        skills = _activator.aktif_skill_listesi()
        if kategori:
            skills = [s for s in skills if kategori.lower() in s.lower()]
        return skills
    except Exception as e:
        logger.warning("Skill listeleme hatasi: %s", e)
        return []

def skill_ekle(ad: str, aciklama: str = "", onem: int = 3) -> str:
    """Yeni skill ekle."""
    try:
        if _activator.skill_var_mi(ad):
            return f"Skill zaten var: {ad}"
        _activator.skill_ekle(ad, aciklama, onem)
        return f"Skill eklendi: {ad}"
    except Exception as e:
        return f"Hata: {e}"

def skill_sil(ad: str) -> str:
    """Skill sil."""
    try:
        _activator.skill_sil(ad)
        return f"Skill silindi: {ad}"
    except Exception as e:
        return f"Hata: {e}"
