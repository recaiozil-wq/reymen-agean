"""Test: reymen/sistem/stt_tool.py"""

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


class TestSTT:
    def test_import(self):
        from reymen.sistem.stt_tool import stt_durum, motor_kaydet

        assert stt_durum is not None

    def test_durum(self):
        from reymen.sistem.stt_tool import stt_durum

        durum = stt_durum()
        assert "faster-whisper" in durum

    def test_motor_kaydet(self):
        from reymen.sistem.stt_tool import motor_kaydet

        m = MockMotor()
        motor_kaydet(m)
        assert "STT_CEVIR" in m.tools
        assert "STT_DURUM" in m.tools
        assert "STT_TEST" in m.tools

    def test_gecersiz_dosya(self):
        from reymen.sistem.stt_tool import sesi_metne_cevir

        sonuc = sesi_metne_cevir("/olmayan/ses.mp3")
        assert "HATA" in sonuc
