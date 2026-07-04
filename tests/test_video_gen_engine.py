"""Test: reymen/arac/video_gen_engine.py"""

from __future__ import annotations
import os, sys, tempfile
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class MockMotor:
    def __init__(self):
        self.tools = {}

    def _plugin_arac_kaydet(self, ad, fonk, aciklama=""):
        self.tools[ad] = fonk


class TestVideoGen:
    def test_import(self):
        from reymen.arac.video_gen_engine import video_uret, video_durum, motor_kaydet

        assert video_uret is not None

    def test_durum(self):
        from reymen.arac.video_gen_engine import video_durum

        durum = video_durum()
        assert "moviepy" in durum

    def test_motor_kaydet(self):
        from reymen.arac.video_gen_engine import motor_kaydet

        m = MockMotor()
        motor_kaydet(m)
        assert "VIDEO_OLUSTUR" in m.tools
        assert "VIDEO_DURUM" in m.tools
        assert "VIDEO_TEST" in m.tools

    def test_bos_resim(self):
        from reymen.arac.video_gen_engine import video_uret

        sonuc = video_uret(resimler=[])
        assert "HATA" in sonuc

    def test_slayt_video(self):
        from reymen.arac.video_gen_engine import video_uret
        import PIL.Image, PIL.ImageDraw

        img = PIL.Image.new("RGB", (320, 240), (50, 50, 80))
        draw = PIL.ImageDraw.Draw(img)
        draw.text((20, 100), "Test", fill=(255, 255, 255))
        tmp = tempfile.mktemp(suffix=".png")
        img.save(tmp)
        try:
            sonuc = video_uret(resimler=[tmp], sure=2)
            assert os.path.exists(sonuc) and os.path.getsize(sonuc) > 0
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
