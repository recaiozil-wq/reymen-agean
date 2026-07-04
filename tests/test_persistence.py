"""Test: reymen/sistem/persistence.py"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestPersistence:
    def test_import(self):
        import reymen.sistem.persistence

        assert reymen.sistem.persistence is not None
