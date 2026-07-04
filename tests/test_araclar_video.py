"""Test: reymen/arac/araclar_video.py - video araclari"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestAraclarVideo:
    def test_import(self):
        import reymen.arac.araclar_video as m

        assert m is not None

    def test_video_bilgi_gecersiz(self):
        from reymen.arac.araclar_video import video_bilgi

        sonuc = video_bilgi("/olmayan/video.mp4")
        assert "bulunamadi" in sonuc.lower() or "hata" in sonuc.lower()

    def test_motor_kaydet(self):
        from reymen.arac.araclar_video import motor_kaydet

        class M:
            tools = {}

            def _plugin_arac_kaydet(self, a, f, d=""):
                self.tools[a] = f

        m = M()
        motor_kaydet(m)
        assert len(m.tools) > 0
