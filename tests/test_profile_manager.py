"""Test: reymen/sistem/profile_manager.py"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestProfileManager:
    def test_import(self):
        from reymen.sistem.profile_manager import ProfileManager

        pm = ProfileManager()
        assert pm is not None
