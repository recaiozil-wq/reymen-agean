"""Test: reymen/arac/web_search_engine.py"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class MockMotor:
    def __init__(self):
        self.tools = {}

    def _plugin_arac_kaydet(self, ad, fonk, aciklama=""):
        self.tools[ad] = fonk


class TestWebSearch:
    def test_import(self):
        from reymen.arac.web_search_engine import motor_kaydet

        assert motor_kaydet is not None

    def test_motor_kaydet(self):
        from reymen.arac.web_search_engine import motor_kaydet

        m = MockMotor()
        motor_kaydet(m)
        assert len(m.tools) > 0
