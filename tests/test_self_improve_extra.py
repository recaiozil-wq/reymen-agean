"""Test: reymen/self_improve.py extended"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestSelfImprove:
    def test_import(self):
        import reymen.self_improve as m

        assert m is not None
