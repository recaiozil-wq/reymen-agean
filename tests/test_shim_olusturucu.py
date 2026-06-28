# -*- coding: utf-8 -*-
"""Tests for shim_olusturucu.py — automatic shim generation for missing modules."""
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import reymen.cereyan.shim_olusturucu as real_mod

from reymen.cereyan.shim_olusturucu import (
    SHIM_DB,
    puan_hesapla,
    kategorilendir,
    _shim_kayitlari,
    _shim_kaydet,
    _shim_olustur,
    shimleri_temizle,
    modul_hatalarini_tara,
    rapor_olustur,
)


# ════════════════════════════════════════════════════════════════
# puan_hesapla
# ════════════════════════════════════════════════════════════════

class TestPuanHesapla:
    def test_100_verir_5(self):
        assert puan_hesapla(100) == 5

    def test_90_verir_5(self):
        assert puan_hesapla(90) == 5

    def test_89_verir_4(self):
        assert puan_hesapla(89) == 4

    def test_70_verir_4(self):
        assert puan_hesapla(70) == 4

    def test_50_verir_3(self):
        assert puan_hesapla(50) == 3

    def test_30_verir_2(self):
        assert puan_hesapla(30) == 2

    def test_10_verir_1(self):
        assert puan_hesapla(15) == 1

    def test_0_verir_0(self):
        assert puan_hesapla(0) == 0

    def test_negatif_verir_0(self):
        assert puan_hesapla(-5) == 0


# ════════════════════════════════════════════════════════════════
# test_kategorisi
# ════════════════════════════════════════════════════════════════

class TestKategori:
    def test_cekirdek_testi(self):
        assert kategorilendir("tests/test_core.py") == "A"

    def test_test_prefix(self):
        assert kategorilendir("test_foo.py") == "A"

    def test_referans_testi(self):
        assert kategorilendir("tests/ReYMeN_reference/agent/test_x.py") == "C"

    def test_referans_prefix(self):
        assert kategorilendir("ReYMeN_reference/test_x.py") == "C"

    def test_skill_testi(self):
        assert kategorilendir("skills/test_x.py") == "B"

    def test_plugin_testi(self):
        assert kategorilendir("plugins/test_x.py") == "B"

    def test_bilinmeyen_diger(self):
        assert kategorilendir("foo/bar/test_x.py") == "B"


# ════════════════════════════════════════════════════════════════
# _shim_kayitlari / _shim_kaydet
# ════════════════════════════════════════════════════════════════

class TestShimKayit:
    def test_db_yoksa_bos_doner(self, tmp_path):
        with patch.object(real_mod, "SHIM_DB", tmp_path / "nonexistent.json"):
            assert _shim_kayitlari() == {}

    def test_db_bossa_bos_doner(self, tmp_path):
        db = tmp_path / "shim_db.json"
        db.write_text("{}", encoding="utf-8")
        with patch.object(real_mod, "SHIM_DB", db):
            assert _shim_kayitlari() == {}

    def test_kaydet_ve_oku(self, tmp_path):
        db = tmp_path / "shim_db.json"
        with patch.object(real_mod, "SHIM_DB", db):
            _shim_kaydet({"test": {"puan": 5}})
            assert _shim_kayitlari() == {"test": {"puan": 5}}

    def test_gecersiz_json_sessiz_hata(self, tmp_path):
        db = tmp_path / "shim_db.json"
        db.write_text("not valid json", encoding="utf-8")
        with patch.object(real_mod, "SHIM_DB", db):
            assert _shim_kayitlari() == {}


# ════════════════════════════════════════════════════════════════
# _shim_olustur
# ════════════════════════════════════════════════════════════════

class TestShimOlustur:
    def test_yeni_shim_olusturur(self, tmp_path):
        with patch.object(real_mod, "ROOT", tmp_path):
            shim_yolu = _shim_olustur("gateway.platforms.base")
            assert shim_yolu is not None
            shim_file = tmp_path / "tools" / "shim" / "gateway" / "platforms" / "base.py"
            assert shim_file.exists()
            assert "StubBase" in shim_file.read_text(encoding="utf-8")

    def test_init_py_olusturulur(self, tmp_path):
        with patch.object(real_mod, "ROOT", tmp_path):
            _shim_olustur("gateway.platforms.base")
            init_file = tmp_path / "tools" / "shim" / "gateway" / "platforms" / "__init__.py"
            assert init_file.exists()
            assert "shim" in init_file.read_text(encoding="utf-8")

    def test_mevcut_shimi_tekrar_olusturmaz(self, tmp_path):
        with patch.object(real_mod, "ROOT", tmp_path):
            ilk = _shim_olustur("gateway.platforms.base")
            ikinci = _shim_olustur("gateway.platforms.base")
            assert ilk == ikinci

    def test_init_pye_export_ekler(self, tmp_path):
        with patch.object(real_mod, "ROOT", tmp_path):
            _shim_olustur("gateway.platforms.base")
            init_file = tmp_path / "tools" / "shim" / "gateway" / "platforms" / "__init__.py"
            icerik = init_file.read_text(encoding="utf-8")
            assert "from .base import *" in icerik

    def test_ikinci_shim_ayri_init_karistirmaz(self, tmp_path):
        with patch.object(real_mod, "ROOT", tmp_path):
            _shim_olustur("gateway.platforms.base")
            _shim_olustur("gateway.platforms.advanced")
            init_file = tmp_path / "tools" / "shim" / "gateway" / "platforms" / "__init__.py"
            icerik = init_file.read_text(encoding="utf-8")
            assert "from .base import *" in icerik
            assert "from .advanced import *" in icerik

    def test_tek_parca_modul(self, tmp_path):
        with patch.object(real_mod, "ROOT", tmp_path):
            shim_yolu = _shim_olustur("missing_module")
            assert shim_yolu is not None
            shim_file = tmp_path / "tools" / "shim" / "missing_module.py"
            assert shim_file.exists()


# ════════════════════════════════════════════════════════════════
# shimleri_temizle
# ════════════════════════════════════════════════════════════════

class TestShimleriTemizle:
    def test_shimleri_siler(self, tmp_path):
        with patch.object(real_mod, "ROOT", tmp_path):
            _shim_olustur("gateway.base")
            shim_dir = tmp_path / "tools" / "shim"
            assert shim_dir.exists()
            shimleri_temizle()
            assert not shim_dir.exists()

    def test_shim_db_de_silinir(self, tmp_path):
        db = tmp_path / "_shim_index.json"
        with patch.object(real_mod, "SHIM_DB", db):
            _shim_kaydet({"test": 1})
            assert db.exists()
            with patch.object(real_mod, "ROOT", tmp_path):
                shimleri_temizle()
                assert not db.exists()

    def test_shim_yoksa_hata_vermez(self, tmp_path):
        with patch.object(real_mod, "ROOT", tmp_path):
            shimleri_temizle()  # should not raise


# ════════════════════════════════════════════════════════════════
# modul_hatalarini_tara
# ════════════════════════════════════════════════════════════════

class TestModulHatalariniTara:
    def test_eksik_modul_yoksa_bos(self, tmp_path):
        sonuclar = {"tests/test_a.py": "PASS", "tests/test_b.py": "PASS"}
        with patch.object(real_mod, "SHIM_DB", tmp_path / "empty.json"):
            _shim_kaydet({"son_hatalar": {}})
            sonuc = modul_hatalarini_tara(sonuclar)
            assert sonuc == []

    def test_sadece_3_tekrar_trigger(self, tmp_path):
        """En az 3 dosyada ayni ModuleNotFoundError olmali."""
        sonuclar = {"tests/test_a.py": "FAIL", "tests/test_b.py": "FAIL"}
        hatalar = {
            "tests/test_a.py": "ModuleNotFoundError: No module named 'foo'",
            "tests/test_b.py": "ModuleNotFoundError: No module named 'foo'",
        }
        with patch.object(real_mod, "SHIM_DB", tmp_path / "db.json"):
            _shim_kaydet({"son_hatalar": hatalar})
            sonuc = modul_hatalarini_tara(sonuclar)
            assert sonuc == []  # sadece 2, 3 gerekli

    def test_3_tekrarda_shim_olusturur(self, tmp_path):
        sonuclar = {"tests/test_a.py": "FAIL", "tests/test_b.py": "FAIL", "tests/test_c.py": "FAIL"}
        hatalar = {
            "tests/test_a.py": "ModuleNotFoundError: No module named 'foo.bar'",
            "tests/test_b.py": "ModuleNotFoundError: No module named 'foo.bar'",
            "tests/test_c.py": "ModuleNotFoundError: No module named 'foo.bar'",
        }
        with patch.object(real_mod, "ROOT", tmp_path):
            with patch.object(real_mod, "SHIM_DB", tmp_path / "db.json"):
                _shim_kaydet({"son_hatalar": hatalar})
                sonuc = modul_hatalarini_tara(sonuclar)
                assert len(sonuc) == 1
                shim_path = str(tmp_path / "tools" / "shim" / "foo" / "bar.py")
                assert sonuc[0] == shim_path

    def test_module_not_found_disinda_yok_say(self, tmp_path):
        sonuclar = {"tests/test_a.py": "FAIL"}
        hatalar = {
            "tests/test_a.py": "ImportError: cannot import name 'X'",
        }
        with patch.object(real_mod, "SHIM_DB", tmp_path / "db.json"):
            _shim_kaydet({"son_hatalar": hatalar})
            sonuc = modul_hatalarini_tara(sonuclar)
            assert sonuc == []


# ════════════════════════════════════════════════════════════════
# rapor_olustur
# ════════════════════════════════════════════════════════════════

class TestRaporOlustur:
    def test_rapor_icerik(self, tmp_path):
        kat_sonuc = {
            "A": {"gecti": 10, "toplam": 10, "puan": 5},
            "B": {"gecti": 8, "toplam": 10, "puan": 4},
            "C": {"gecti": 5, "toplam": 10, "puan": 3},
        }
        with patch.object(real_mod, "ROOT", tmp_path):
            rapor = rapor_olustur(
                gecti=23, basarisiz=5, timeout=2, toplam=30,
                kategori_sonuc=kat_sonuc, shim_sayisi=3,
            )
            assert "REYMEN TEST SONUC RAPORU" in rapor
            assert "Toplam: 30" in rapor
            assert "GECTI: 23" in rapor
            assert "AKTIF SHIM: 3" in rapor
            assert "GENEL PUAN: 12/15" in rapor

    def test_rapor_dosyaya_yazilir(self, tmp_path):
        kat_sonuc = {"A": {"gecti": 5, "toplam": 5, "puan": 5}}
        with patch.object(real_mod, "ROOT", tmp_path):
            rapor_olustur(5, 0, 0, 5, kat_sonuc, 0)
            rapor_file = tmp_path / "_test_raporu.txt"
            assert rapor_file.exists()
            icerik = rapor_file.read_text(encoding="utf-8")
            assert "Toplam: 5" in icerik

    def test_bos_rapor_hata_vermez(self, tmp_path):
        kat_sonuc = {}
        with patch.object(real_mod, "ROOT", tmp_path):
            rapor = rapor_olustur(0, 0, 0, 0, kat_sonuc, 0)
            assert "BASARI ORANI: 0%" in rapor
