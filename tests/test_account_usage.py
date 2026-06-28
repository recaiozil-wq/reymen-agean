# -*- coding: utf-8 -*-
"""tests/test_account_usage.py — AccountUsage kapsamlı test."""

import json
import os
import sys
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestAccountUsageInit:
    """AccountUsage başlangıç durumu."""

    def test_bos_baslangic(self, tmp_path):
        with patch("reymen.sistem.account_usage.RAPOR_DOSYASI", tmp_path / "usage.json"):
            from reymen.sistem.account_usage import AccountUsage
            h = AccountUsage()
            assert h._veri["toplam_istek"] == 0
            assert h._veri["toplam_token"] == 0
            assert h._veri["toplam_maliyet"] == 0.0
            assert h._veri["providerlar"] == {}
            assert h._veri["aylik_veri"] == {}

    def test_mevcut_dosyadan_yukle(self, tmp_path):
        dosya = tmp_path / "usage.json"
        veri = {
            "olusturma": "2026-01-01",
            "toplam_istek": 5,
            "toplam_token": 1000,
            "toplam_maliyet": 0.05,
            "providerlar": {"deepseek": {"istek": 5, "token": 1000, "maliyet": 0.05, "model": "chat"}},
            "aylik_veri": {},
        }
        dosya.write_text(json.dumps(veri), encoding="utf-8")
        with patch("reymen.sistem.account_usage.RAPOR_DOSYASI", dosya):
            from reymen.sistem.account_usage import AccountUsage
            h = AccountUsage()
            assert h._veri["toplam_istek"] == 5
            assert h._veri["toplam_maliyet"] == 0.05

    def test_bozuk_json_sifirlama(self, tmp_path):
        dosya = tmp_path / "usage.json"
        dosya.write_text("{bozuk json!!!", encoding="utf-8")
        with patch("reymen.sistem.account_usage.RAPOR_DOSYASI", dosya):
            from reymen.sistem.account_usage import AccountUsage
            h = AccountUsage()
            assert h._veri["toplam_istek"] == 0


class TestEkle:
    """ekle() — kullanım kaydı ekleme."""

    def _make(self, tmp_path):
        with patch("reymen.sistem.account_usage.RAPOR_DOSYASI", tmp_path / "usage.json"):
            from reymen.sistem.account_usage import AccountUsage
            return AccountUsage()

    def test_ekle_tek(self, tmp_path):
        h = self._make(tmp_path)
        h.ekle("deepseek", "chat", 100, 50, 0.001)
        assert h._veri["toplam_istek"] == 1
        assert h._veri["toplam_token"] == 150
        assert h._veri["toplam_maliyet"] == 0.001

    def test_ekle_coklu(self, tmp_path):
        h = self._make(tmp_path)
        h.ekle("deepseek", "chat", 100, 50, 0.001)
        h.ekle("deepseek", "chat", 200, 100, 0.002)
        assert h._veri["toplam_istek"] == 2
        assert h._veri["toplam_token"] == 450

    def test_provider_kaydi(self, tmp_path):
        h = self._make(tmp_path)
        h.ekle("deepseek", "chat", 100, 50, 0.001)
        p = h._veri["providerlar"]["deepseek"]
        assert p["istek"] == 1
        assert p["token"] == 150
        assert p["model"] == "chat"

    def test_aylik_kaydi(self, tmp_path):
        h = self._make(tmp_path)
        h.ekle("deepseek", "chat", 100, 50, 0.001)
        ay = date.today().isoformat()[:7]
        assert ay in h._veri["aylik_veri"]
        a = h._veri["aylik_veri"][ay]
        assert a["istek"] == 1
        assert a["token"] == 150

    def test_maliyet_yuvarlama(self, tmp_path):
        h = self._make(tmp_path)
        h.ekle("test", "m", 1, 1, 0.0001)
        h.ekle("test", "m", 1, 1, 0.0002)
        # round(0.0001 + 0.0002, 4) = 0.0003
        assert h._veri["toplam_maliyet"] == 0.0003


class TestOzet:
    """ozet() — özet string."""

    def test_ozet_format(self, tmp_path):
        with patch("reymen.sistem.account_usage.RAPOR_DOSYASI", tmp_path / "usage.json"):
            from reymen.sistem.account_usage import AccountUsage
            h = AccountUsage()
            h.ekle("deepseek", "chat", 100, 50, 0.001)
            sonuc = h.ozet()
            assert "Toplam istek: 1" in sonuc
            assert "deepseek" in sonuc


class TestProviderRaporu:
    """provider_raporu() — provider detayı."""

    def test_meveut_provider(self, tmp_path):
        with patch("reymen.sistem.account_usage.RAPOR_DOSYASI", tmp_path / "usage.json"):
            from reymen.sistem.account_usage import AccountUsage
            h = AccountUsage()
            h.ekle("deepseek", "chat", 100, 50, 0.001)
            sonuc = h.provider_raporu("deepseek")
            assert "deepseek" in sonuc
            assert "chat" in sonuc

    def test_olmayan_provider(self, tmp_path):
        with patch("reymen.sistem.account_usage.RAPOR_DOSYASI", tmp_path / "usage.json"):
            from reymen.sistem.account_usage import AccountUsage
            h = AccountUsage()
            sonuc = h.provider_raporu("yok")
            assert "kaydi yok" in sonuc.lower() or "yok" in sonuc.lower()


class TestAylikRapor:
    """aylik_rapor() — aylık rapor."""

    def test_meveut_ay(self, tmp_path):
        with patch("reymen.sistem.account_usage.RAPOR_DOSYASI", tmp_path / "usage.json"):
            from reymen.sistem.account_usage import AccountUsage
            h = AccountUsage()
            h.ekle("deepseek", "chat", 100, 50, 0.001)
            ay = date.today().isoformat()[:7]
            sonuc = h.aylik_rapor(ay)
            assert ay in sonuc

    def test_olmayan_ay(self, tmp_path):
        with patch("reymen.sistem.account_usage.RAPOR_DOSYASI", tmp_path / "usage.json"):
            from reymen.sistem.account_usage import AccountUsage
            h = AccountUsage()
            sonuc = h.aylik_rapor("2020-01")
            assert "kayit yok" in sonuc.lower() or "2020-01" in sonuc


class TestButceUyarisi:
    """butce_uyarisi() — bütçe kontrolü."""

    def _make_with_data(self, tmp_path, maliyet):
        with patch("reymen.sistem.account_usage.RAPOR_DOSYASI", tmp_path / "usage.json"):
            from reymen.sistem.account_usage import AccountUsage
            h = AccountUsage()
            # Fake the monthly data directly
            ay = date.today().isoformat()[:7]
            h._veri["aylik_veri"][ay] = {"istek": 10, "token": 5000, "maliyet": maliyet}
            return h

    def test_limit_alti(self, tmp_path):
        h = self._make_with_data(tmp_path, 5.0)
        assert h.butce_uyarisi(10.0) is None

    def test_limit_asimi(self, tmp_path):
        h = self._make_with_data(tmp_path, 12.0)
        sonuc = h.butce_uyarisi(10.0)
        assert sonuc is not None
        assert "asildi" in sonuc.lower() or "12" in sonuc

    def test_yuzde80_uyarisi(self, tmp_path):
        h = self._make_with_data(tmp_path, 8.5)
        sonuc = h.butce_uyarisi(10.0)
        assert sonuc is not None
        assert "80" in sonuc or "%" in sonuc

    def test_kayit_yok(self, tmp_path):
        h = self._make_with_data(tmp_path, 0.0)
        # Remove the aylik data
        h._veri["aylik_veri"] = {}
        assert h.butce_uyarisi(10.0) is None


class TestSifirla:
    """sifirla() — veri sıfırlama."""

    def test_sifirla(self, tmp_path):
        with patch("reymen.sistem.account_usage.RAPOR_DOSYASI", tmp_path / "usage.json"):
            from reymen.sistem.account_usage import AccountUsage
            h = AccountUsage()
            h.ekle("deepseek", "chat", 100, 50, 0.001)
            assert h._veri["toplam_istek"] == 1
            h.sifirla()
            assert h._veri["toplam_istek"] == 0
            assert h._veri["toplam_maliyet"] == 0.0
            assert h._veri["providerlar"] == {}


class TestGlobalFonksiyonlar:
    """hesap_ekle / hesap_ozet global fonksiyonları."""

    def test_hesap_ozet_donus_tipi(self, tmp_path):
        with patch("reymen.sistem.account_usage.RAPOR_DOSYASI", tmp_path / "usage.json"):
            from reymen.sistem.account_usage import hesap_ozet
            sonuc = hesap_ozet()
            assert isinstance(sonuc, str)
            assert "Hesap" in sonuc or "istek" in sonuc.lower()
