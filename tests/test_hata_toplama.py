"""Test: reymen/sistem/hata_toplama.py"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestHataToplama:
    def test_import(self):
        import reymen.sistem.hata_toplama as m

        assert m is not None
