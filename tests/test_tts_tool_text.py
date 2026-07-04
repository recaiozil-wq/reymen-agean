"""Test: reymen/sistem/tts_tool_text.py"""

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


class TestTTS:
    def test_import(self):
        from reymen.sistem.tts_tool_text import (
            metni_sese_cevir,
            ses_listesi,
            motor_kaydet,
        )

        assert metni_sese_cevir is not None

    def test_ses_listesi(self):
        from reymen.sistem.tts_tool_text import ses_listesi

        sesler = ses_listesi("tr")
        assert "Emel" in sesler or "tr-TR" in sesler

    def test_motor_kaydet(self):
        from reymen.sistem.tts_tool_text import motor_kaydet

        m = MockMotor()
        motor_kaydet(m)
        assert "TTS_KONUS" in m.tools
        assert "TTS_SESLER" in m.tools
        assert "TTS_TEST" in m.tools

    def test_bos_metin(self):
        from reymen.sistem.tts_tool_text import metni_sese_cevir

        sonuc = metni_sese_cevir("")
        assert "HATA" in sonuc
