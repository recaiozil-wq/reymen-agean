"""Test: reymen/self_improve.py - kapsamli"""

from __future__ import annotations
import os, sys, tempfile
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestSelfImproveKapsamli:
    def test_import(self):
        from reymen.self_improve import SelfImprove

        assert SelfImprove is not None

    def test_olustur(self):
        from reymen.self_improve import SelfImprove

        si = SelfImprove()
        assert si is not None

    def test_kayit_ekle(self):
        from reymen.self_improve import SelfImprove

        si = SelfImprove()
        si.kayit_ekle("test_meta", {"test": "veri"})
        # Hata vermemeli
        assert True

    def test_son_kayit(self):
        from reymen.self_improve import SelfImprove

        si = SelfImprove()
        si.kayit_ekle("meta1", {"d": "1"})
        si.kayit_ekle("meta2", {"d": "2"})
        son = si.son_kayit()
        assert son is not None
