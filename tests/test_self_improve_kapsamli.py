"""Test: reymen/self_improve.py - kapsamli"""

from __future__ import annotations
import os, sys, tempfile
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestSelfImproveKapsamli:
    def test_import(self):
        from reymen.self_improve import SelfImprover

        assert SelfImprover is not None

    def test_olustur(self):
        from reymen.self_improve import SelfImprover

        si = SelfImprover()
        assert si is not None

    def test_kayit_ekle(self):
        from reymen.self_improve import SelfImprover

        si = SelfImprover()
        si.record("test_meta", {"test": "veri"})
        assert True

    def test_son_kayit(self):
        from reymen.self_improve import SelfImprover

        si = SelfImprover()
        si.record("meta1", {"d": "1"})
        si.record("meta2", {"d": "2"})
        son = si.history()
        assert son is not None
