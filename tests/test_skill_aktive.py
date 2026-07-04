"""Test: reymen/sistem/skill_aktive_et.py"""

from __future__ import annotations
import os
import sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestSkillAktive:
    def test_aktif_skill_sayisi(self):
        from reymen.sistem.skill_aktive_et import aktif_skill_sayisi

        sayi = aktif_skill_sayisi()
        assert isinstance(sayi, int)

    def test_skill_aktif_et_none(self):
        from reymen.sistem.skill_aktive_et import skill_aktif_et

        sonuc = skill_aktif_et("xyz_olmayan_skill_12345")
        assert sonuc is None

    def test_motor_kaydet(self):
        from reymen.sistem.skill_aktive_et import motor_kaydet

        assert callable(motor_kaydet)

    def test_motor_kaydet_registers(self):
        from reymen.sistem.skill_aktive_et import motor_kaydet

        mm = MockMotor()
        motor_kaydet(mm)
        assert "SKILL_AKTIF" in mm.tools


class MockMotor:
    def __init__(self):
        self.tools = {}

    def _plugin_arac_kaydet(self, ad, fonk, aciklama=""):
        self.tools[ad] = fonk

    def tool_kaydet(self, ad, fonk, aciklama="", tur="islev"):
        self.tools[ad] = fonk
