"""Test: reymen/sistem/self_improve.py + self_improvement.py"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestSelfImprove:
    def test_import_sistem(self):
        import reymen.self_improve

        assert reymen.self_improve is not None

    def test_import_cereyan(self):
        import reymen.cereyan.self_improvement

        assert reymen.cereyan.self_improvement is not None
