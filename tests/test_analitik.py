"""Test: reymen/sistem/analitik.py"""

from __future__ import annotations
import os, sys, tempfile, importlib
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestAnalitik:
    def test_import(self):
        import reymen.sistem.analitik

        assert reymen.sistem.analitik is not None

    def test_motor_kaydet(self):
        from reymen.sistem.analitik import motor_kaydet

        mm = MockMotor()
        motor_kaydet(mm)
        assert "ANALITIK_KAYDET" in mm.tools


class MockMotor:
    def __init__(self):
        self.tools = {}

    def _plugin_arac_kaydet(self, a, f, ac="", tur="islev"):
        self.tools[a] = f
