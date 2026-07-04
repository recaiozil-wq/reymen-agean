"""Test: reymen/sistem/surekli_ogrenme.py"""

from __future__ import annotations
import json
import os
import sys
import tempfile
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestOgrenmeModel:
    def test_ogrenme_olustur(self):
        from reymen.sistem.surekli_ogrenme import Ogrenme

        o = Ogrenme(alan="test", icerik="deneme", kaynak="pytest")
        assert o.alan == "test"
        assert o.icerik == "deneme"
        assert o.kaynak == "pytest"

    def test_ogrenme_to_dict(self):
        from reymen.sistem.surekli_ogrenme import Ogrenme

        o = Ogrenme(alan="test", icerik="içerik", etiketler=["a", "b"])
        d = o.to_dict()
        assert d["alan"] == "test"
        assert d["icerik"] == "içerik"
        assert "a" in d["etiketler"]
        assert "zaman" in d

    def test_ogrenme_from_dict(self):
        from reymen.sistem.surekli_ogrenme import Ogrenme

        data = {
            "alan": "test",
            "icerik": "xyz",
            "kaynak": "manual",
            "etiketler": [],
            "zaman": "2026-01-01T00:00:00",
        }
        o = Ogrenme.from_dict(data)
        assert o.alan == "test"
        assert o.icerik == "xyz"


class TestOgrenmeDeposu:
    def test_depo_olustur(self):
        from reymen.sistem.surekli_ogrenme import OgrenmeDeposu

        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            depo = OgrenmeDeposu(dosya=Path(tmp_path))
            assert depo is not None
        finally:
            os.unlink(tmp_path)

    def test_kaydet_ve_getir(self):
        from reymen.sistem.surekli_ogrenme import OgrenmeDeposu, Ogrenme

        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            depo = OgrenmeDeposu(dosya=Path(tmp_path))
            o = Ogrenme(alan="test_alan", icerik="test_icerik")
            assert depo.kaydet(o) is True

            hepsi = depo.hepsini_getir()
            assert len(hepsi) == 1
            assert hepsi[0].alan == "test_alan"
        finally:
            os.unlink(tmp_path)

    def test_alan_listesi(self):
        from reymen.sistem.surekli_ogrenme import OgrenmeDeposu, Ogrenme

        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            depo = OgrenmeDeposu(dosya=Path(tmp_path))
            depo.kaydet(Ogrenme(alan="a1", icerik="x"))
            depo.kaydet(Ogrenme(alan="a2", icerik="y"))
            depo.kaydet(Ogrenme(alan="a1", icerik="z"))
            alanlar = depo.alan_listesi()
            assert "a1" in alanlar
            assert "a2" in alanlar
            assert depo.sayi() == 3
        finally:
            os.unlink(tmp_path)


class TestSurekliOgrenmeYoneticisi:
    def test_yonetici_olustur(self):
        from reymen.sistem.surekli_ogrenme import SurekliOgrenmeYoneticisi

        y = SurekliOgrenmeYoneticisi()
        assert y is not None

    def test_ogren_ve_hatirla(self):
        from reymen.sistem.surekli_ogrenme import SurekliOgrenmeYoneticisi

        y = SurekliOgrenmeYoneticisi()
        sonuc = y.ogren("test_alan", "test_bilgi")
        assert isinstance(sonuc, str)

        hatirlanan = y.hatirla("test_alan")
        assert "test_bilgi" in hatirlanan

    def test_ozet(self):
        from reymen.sistem.surekli_ogrenme import SurekliOgrenmeYoneticisi

        y = SurekliOgrenmeYoneticisi()
        o = y.ozet()
        assert isinstance(o, str)

    def test_get_yonetici(self):
        from reymen.sistem.surekli_ogrenme import get_yonetici

        y = get_yonetici()
        assert y is not None


class TestMotorEntegrasyonu:
    def test_motor_kaydet(self):
        from reymen.sistem.surekli_ogrenme import motor_kaydet

        assert callable(motor_kaydet)

    def test_motor_kaydet_registers(self):
        from reymen.sistem.surekli_ogrenme import motor_kaydet

        mm = MockMotor()
        motor_kaydet(mm)
        assert "OGREN" in mm.tools
        assert "OGRENMELERI_GETIR" in mm.tools
        assert "OGRENME_OZETI" in mm.tools


class MockMotor:
    def __init__(self):
        self.tools = {}

    def tool_kaydet(self, ad, fonk, aciklama="", tur="islev"):
        self.tools[ad] = fonk

    def _plugin_arac_kaydet(self, ad, fonk, aciklama=""):
        self.tools[ad] = fonk
