"""Test: reymen/a2a.py ve a2a_integration.py entegre"""

from __future__ import annotations
import os, sys, threading
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestA2AEntegre:
    def test_a2a_import(self):
        import reymen.a2a as m

        assert m is not None

    def test_a2a_integration_import(self):
        import reymen.a2a_integration as m

        assert m is not None

    def test_mesaj_kuyrugu(self):
        from reymen.a2a import A2A

        a2a = A2A()
        a2a.mesaj_yolla("test_hedef", "test_icerik")
        mesajlar = a2a.mesajlari_al("test_hedef")
        assert len(mesajlar) > 0
        assert mesajlar[0]["icerik"] == "test_icerik"

    def test_mesaj_sil(self):
        from reymen.a2a import A2A

        a2a = A2A()
        a2a.mesaj_yolla("test_hedef2", "silinecek")
        a2a.mesajlari_temizle("test_hedef2")
        mesajlar = a2a.mesajlari_al("test_hedef2")
        assert len(mesajlar) == 0

    def test_birden_fazla_mesaj(self):
        from reymen.a2a import A2A

        a2a = A2A()
        a2a.mesaj_yolla("h", "m1")
        a2a.mesaj_yolla("h", "m2")
        a2a.mesaj_yolla("h", "m3")
        mesajlar = a2a.mesajlari_al("h")
        assert len(mesajlar) == 3
