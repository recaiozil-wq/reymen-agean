#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_memory_manager.py — MemoryManager birim testleri."""

import sys
sys.path.insert(0, ".")

from agent.memory_manager import MemoryManager, memory_manager


class TestMemoryManagerInit:
    """Baslatma testleri."""

    def test_init_bos_config(self):
        mm = MemoryManager({})
        assert mm._max_kayit == 2000
        assert mm._aktif is True
        assert mm.ping() is True

    def test_init_ozel_config(self):
        mm = MemoryManager({"memory": {"max_records": 1000}})
        assert mm._max_kayit == 1000

    def test_init_config_yok(self):
        mm = MemoryManager()
        assert mm._max_kayit == 2000

    def test_singleton(self):
        mm1 = memory_manager({"memory": {}})
        mm2 = memory_manager()
        assert mm1 is mm2


class TestMemoryManagerKomut:
    """/hafiza komutu testleri."""

    def test_komut_bos(self):
        mm = MemoryManager({})
        r = mm.komut_islem("")
        assert "ReYMeN Hafiza" in r
        assert "Komutlar" in r

    def test_komut_durum(self):
        mm = MemoryManager({})
        r = mm.komut_islem("durum")
        assert "ReYMeN Hafiza" in r

    def test_komut_status(self):
        mm = MemoryManager({})
        r = mm.komut_islem("status")
        assert "ReYMeN Hafiza" in r

    def test_komut_kaydet_bos(self):
        mm = MemoryManager({})
        r = mm.komut_islem("kaydet")
        assert "Kullanim" in r

    def test_komut_kaydet(self):
        mm = MemoryManager({})
        r = mm.komut_islem("kaydet Bu bir test kaydidir")
        assert "[Hafiza]" in r

    def test_komut_ara_bos(self):
        mm = MemoryManager({})
        r = mm.komut_islem("ara")
        assert "Kullanim" in r

    def test_komut_ara(self):
        mm = MemoryManager({})
        r = mm.komut_islem("ara test")
        assert "[Hafiza]" in r

    def test_komut_istatistik(self):
        mm = MemoryManager({})
        r = mm.komut_islem("istatistik")
        assert "Istatistik" in r
        assert "Aktif" in r

    def test_komut_bilinmeyen(self):
        mm = MemoryManager({})
        r = mm.komut_islem("olmayan_komut")
        assert "Bilinmeyen" in r


class TestMemoryManagerIslem:
    """Hafiza islem testleri."""

    def test_kaydet_task(self):
        mm = MemoryManager({})
        r = mm.kaydet("test_anahtar", "test icerik", tur="task")
        assert "[Hafiza]" in r

    def test_kaydet_vector(self):
        mm = MemoryManager({})
        r = mm.kaydet("vec_test", "vektor icerik", tur="vector")
        assert "[Hafiza]" in r

    def test_kaydet_longterm(self):
        mm = MemoryManager({})
        r = mm.kaydet("long_test", "uzun sureli icerik", tur="longterm")
        assert "[Hafiza]" in r

    def test_kaydet_gecersiz_tur(self):
        mm = MemoryManager({})
        r = mm.kaydet("x", "y", tur="olmayan")
        assert "Bilinmeyen" in r

    def test_ara_bos(self):
        mm = MemoryManager({})
        r = mm.ara("olmayan_sorgu_12345")
        assert r == []

    def test_durum(self):
        mm = MemoryManager({})
        d = mm.durum()
        assert "aktif" in d
        assert "max_kayit" in d
        assert d["aktif"] is True
