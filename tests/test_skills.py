"""Test: reymen/arac/skill_utils.py"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestSkills:
    def test_import(self):
        import reymen.arac.skill_utils

        assert reymen.arac.skill_utils is not None
