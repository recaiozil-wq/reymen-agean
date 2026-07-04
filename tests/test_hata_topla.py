"""Test: reymen/sistem/hata_topla.py"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestHata:
    def test_import(self):
        import reymen.sistem.hata_topla

        assert reymen.sistem.hata_topla is not None
