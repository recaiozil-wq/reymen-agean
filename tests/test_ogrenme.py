# -*- coding: utf-8 -*-
"""Test: ogrenme.py — Hata cozum hafizasi (SQLite, TTL, imza)."""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
from src.core.ogrenme import (
    imza_uret,
    cozum_bul,
    cozum_kaydet,
    tablo_olustur,
    ttl_temizle,
    istatistik,
    backoff_bekle,
    OgrenmeDongusu,
)
import src.core.ogrenme as _ogrenme_mod


# ── Test Fixtures ─────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _test_db(monkeypatch, tmp_path):
    """Her test ayri gecici DB kullansin."""
    fake_db = tmp_path / "test_hafiza.db"
    monkeypatch.setattr(_ogrenme_mod, "DB_PATH", fake_db)
    tablo_olustur()
    yield


# ── Imza Testleri ─────────────────────────────────────────────


class TestImza:
    def test_imza_uret_string(self):
        hata = ValueError("test hatasi")
        imza = imza_uret(hata)
        assert isinstance(imza, str)
        assert len(imza) == 16
        assert all(c in "0123456789abcdef" for c in imza)

    def test_imza_urette_soyutlama(self):
        h1 = FileNotFoundError("/some/path/file.txt")
        h2 = FileNotFoundError("/other/path/data.csv")
        assert imza_uret(h1) == imza_uret(h2), "Soyutlama calismali"

    def test_gecersiz_imza_tip(self):
        with pytest.raises(AttributeError):
            imza_uret("bu bir exception degil")


# ── Cozum Islemi Testleri ─────────────────────────────────────


class TestCozumKaydetVeBul:
    def test_kaydet_ve_bul(self):
        imza = "test_imza_001"
        cozum_kaydet(
            imza,
            "ValueError",
            "test hatasi",
            "cozum_kodu_ornek",
            "test.py",
            basarili=True,
        )
        bulunan = cozum_bul(imza)
        assert bulunan == "cozum_kodu_ornek"

    def test_kaydet_basarisiz_bulunamaz(self):
        imza = "test_imza_basarisiz"
        cozum_kaydet(imza, "TypeError", "tip hatasi", "", "test.py", basarili=False)
        assert cozum_bul(imza) is None

    def test_gecersiz_imza_bul(self):
        assert cozum_bul("olmayan_imza_xyz_123") is None


# ── Yardimci Fonksiyon Testleri ───────────────────────────────


class TestYardimcilar:
    def test_istatistik_sifir(self):
        stats = istatistik()
        assert stats["toplam"] == 0
        assert stats["basarili"] == 0

    def test_backoff_bekle_usseldir(self):
        b1 = backoff_bekle(1)
        b2 = backoff_bekle(2)
        b3 = backoff_bekle(3)
        assert b1 < b2 < b3
        assert b1 == 1.0
        assert b2 == 2.0
        assert b3 == 4.0

    def test_ttl_temizle_bos(self):
        silinen = ttl_temizle()
        assert silinen == 0


# ── Ogrenme Dongusu Testleri ──────────────────────────────────


class TestOgrenmeDongusu:
    def test_ogrenme_dongusu_baslatma(self):
        dongu = OgrenmeDongusu(max_deneme=2)
        stats = dongu.istatistik()
        assert stats["toplam_ogrenme"] == 0
        assert stats["basari_orani"] == 0
