# -*- coding: utf-8 -*-
"""Tests for budget_config.py — BudgetConfig class."""

import pytest
import os
import time
import json
import tempfile
from unittest.mock import patch


# Import from the real module (not shim)
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from reymen.sistem.budget_config import BudgetConfig, run


class TestBudgetConfigInit:
    """__init__ testleri."""

    def test_varsayilan_limitler(self):
        bc = BudgetConfig()
        assert bc._limitler == BudgetConfig.VARSAYILAN_LIMITLER

    def test_kayit_yolu_param(self):
        bc = BudgetConfig(kayit_yolu="/tmp/test.json")
        assert bc._kayit_yolu == "/tmp/test.json"

    def test_baslangic_sifir(self):
        bc = BudgetConfig()
        assert bc._toplam_kullanim == 0.0
        assert bc._kullanim == {}

    def test_env_override(self):
        with patch.dict(os.environ, {"ReYMeN_BUDGET_GUNLUK_TOKEN": "999"}):
            bc = BudgetConfig()
            assert bc._limitler["gunluk_token"] == 999.0

    def test_env_invalid_uses_default(self):
        with patch.dict(os.environ, {"ReYMeN_BUDGET_GUNLUK_API": "not_a_number"}):
            bc = BudgetConfig()
            assert bc._limitler["gunluk_api"] == BudgetConfig.VARSAYILAN_LIMITLER["gunluk_api"]


class TestButceAyarlama:
    """butce_ayarla testleri."""

    def test_yeni_tip_ekle(self):
        bc = BudgetConfig()
        msg = bc.butce_ayarla("ozel_limit", 500)
        assert "500" in msg
        assert bc._limitler["ozel_limit"] == 500.0

    def test_var_olan_tip_degistir(self):
        bc = BudgetConfig()
        bc.butce_ayarla("gunluk_token", 200)
        assert bc._limitler["gunluk_token"] == 200.0

    def test_negatif_limit(self):
        bc = BudgetConfig()
        msg = bc.butce_ayarla("test", -10)
        assert "negatif" in msg.lower()

    def test_sifir_limit(self):
        bc = BudgetConfig()
        msg = bc.butce_ayarla("test", 0)
        assert "ayarlandi" in msg.lower()
        assert bc._limitler["test"] == 0.0


class TestButceKullanim:
    """butce_kullan testleri."""

    def test_normal_kullanim(self):
        bc = BudgetConfig()
        bc.butce_ayarla("test", 100)
        msg = bc.butce_kullan(30, "test")
        assert "30" in msg
        assert bc._kullanim["test"] == 30.0

    def test_kumulatif(self):
        bc = BudgetConfig()
        bc.butce_ayarla("test", 100)
        bc.butce_kullan(10, "test")
        bc.butce_kullan(20, "test")
        assert bc._kullanim["test"] == 30.0

    def test_limit_asimi(self):
        bc = BudgetConfig()
        bc.butce_ayarla("test", 100)
        msg = bc.butce_kullan(150, "test")
        assert "UYARI" in msg or "asildi" in msg.lower()
        assert bc._kullanim["test"] == 150.0

    def test_negatif_kullanim(self):
        bc = BudgetConfig()
        bc.butce_ayarla("test", 100)
        msg = bc.butce_kullan(-10, "test")
        assert "negatif" in msg.lower()

    def test_tanimsiz_tip(self):
        bc = BudgetConfig()
        msg = bc.butce_kullan(10, "olmayan_tip")
        assert "tanimli degil" in msg.lower()

    def test_uyari_esigi(self):
        bc = BudgetConfig()
        bc.butce_ayarla("test", 100)
        # 85 kullan -> %85 -> uyari esigi (%80) asildi
        msg = bc.butce_kullan(85, "test")
        assert "UYARI" in msg or "yaklasiyor" in msg.lower()

    def test_toplam_kullanim_arttir(self):
        bc = BudgetConfig()
        bc.butce_ayarla("test", 100)
        bc.butce_kullan(10, "test")
        bc.butce_kullan(20, "test")
        assert bc._toplam_kullanim == 30.0


class TestKalanButce:
    """kalan_butce testleri."""

    def test_kalan_hesaplama(self):
        bc = BudgetConfig()
        bc.butce_ayarla("test", 100)
        bc.butce_kullan(30, "test")
        assert bc.kalan_butce("test") == 70.0

    def test_tanimsiz_tip(self):
        bc = BudgetConfig()
        assert bc.kalan_butce("olmayan") == 0.0

    def test_sifir_kullanim(self):
        bc = BudgetConfig()
        assert bc.kalan_butce("gunluk_token") == 100000.0


class TestSifirlama:
    """sifirla testleri."""

    def test_tek_tip_sifirla(self):
        bc = BudgetConfig()
        bc.butce_ayarla("test", 100)
        bc.butce_kullan(50, "test")
        msg = bc.sifirla("test")
        assert bc._kullanim["test"] == 0
        assert "50" in msg

    def test_tumunu_sifirla(self):
        bc = BudgetConfig()
        bc.butce_ayarla("test1", 100)
        bc.butce_ayarla("test2", 200)
        bc.butce_kullan(50, "test1")
        bc.butce_kullan(100, "test2")
        msg = bc.sifirla()
        assert bc._kullanim == {}
        assert bc._toplam_kullanim == 0

    def test_sifirlanamayan_tip(self):
        bc = BudgetConfig()
        msg = bc.sifirla("olmayan")
        assert "yok" in msg.lower()


class TestButceGetir:
    """butce_getir testleri."""

    def test_tek_tip_getir(self):
        bc = BudgetConfig()
        bc.butce_ayarla("test", 100)
        bc.butce_kullan(30, "test")
        sonuc = bc.butce_getir("test")
        assert sonuc["limit"] == 100
        assert sonuc["kullanim"] == 30
        assert sonuc["kalan"] == 70.0

    def test_tumunu_getir(self):
        bc = BudgetConfig()
        sonuc = bc.butce_getir()
        assert "gunluk_token" in sonuc
        assert "gunluk_api" in sonuc

    def test_tanimsiz_tip_getir(self):
        bc = BudgetConfig()
        sonuc = bc.butce_getir("olmayan")
        assert "hata" in sonuc


class TestListeVeOzet:
    """liste_tipleri ve ozet testleri."""

    def test_liste(self):
        bc = BudgetConfig()
        tipler = bc.liste_tipleri()
        assert isinstance(tipler, list)
        assert "gunluk_token" in tipler

    def test_ozet(self):
        bc = BudgetConfig()
        ozet = bc.ozet()
        assert "toplam_kullanim" in ozet
        assert "aktif_limitler" in ozet
        assert "tipler" in ozet


class TestRun:
    """run() CLI fonksiyonu testleri."""

    def test_run_ozet(self):
        sonuc = run(islem="ozet")
        assert isinstance(sonuc, str)
        parsed = json.loads(sonuc)
        assert "toplam_kullanim" in parsed

    def test_run_ayarla(self):
        sonuc = run(islem="butce_ayarla", tip="test_run", limit=500)
        assert "ayarlandi" in sonuc.lower()

    def test_run_kullan(self):
        # run() creates new BudgetConfig each time — use defaults
        sonuc = run(islem="butce_kullan", tip="gunluk_token", adet=25)
        assert "25" in sonuc

    def test_run_kalan(self):
        sonuc = run(islem="kalan_butce", tip="gunluk_token")
        # Default is 100000, no usage yet
        assert "100000" in sonuc or "100000.0" in sonuc

    def test_run_sifirla(self):
        sonuc = run(islem="sifirla", tip="gunluk_token")
        assert "sifirlandi" in sonuc.lower() or "yok" in sonuc.lower()

    def test_run_liste(self):
        sonuc = run(islem="liste")
        assert "gunluk_token" in sonuc
