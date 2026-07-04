# -*- coding: utf-8 -*-
"""Test: ogrenme.py — Hata cozum hafizasi (SQLite, TTL, imza)."""

import sys
import os

# Proje kokunu ekle
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


# ── Test Fixtures ─────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _test_db(monkeypatch, tmp_path):
    """Her test ayri gecici DB kullansin."""
    fake_db = str(tmp_path / "test_hafiza.db")
    monkeypatch.setattr("reymen.core.ogrenme.DB_PATH", tmp_path / "test_hafiza.db")
    tablo_olustur()
    yield
    # Temizlik
    if (tmp_path / "test_hafiza.db").exists():
        (tmp_path / "test_hafiza.db").unlink()


# ── Imza Testleri ─────────────────────────────────────────────


class TestImza:
    """imza_uret — exception'dan soyut imza olusturma."""

    def test_imza_uret_string(self):
        """Happy path: imza 16 karakterli hex string olmali."""
        hata = ValueError("test hatasi")
        imza = imza_uret(hata)
        assert isinstance(imza, str)
        assert len(imza) == 16
        assert all(c in "0123456789abcdef" for c in imza)

    def test_imza_urette_soyutlama(self):
        """Happy path: ayni tip hata ayni imzayi verir."""
        h1 = FileNotFoundError("/some/path/file.txt")
        h2 = FileNotFoundError("/other/path/data.csv")
        assert imza_uret(h1) == imza_uret(h2), "Soyutlama calismali"

    def test_gecersiz_imza_tip(self):
        """Error case: imza_uret exception disi arguman alirsa hata."""
        with pytest.raises(AttributeError):
            imza_uret("bu bir exception degil")  # str'in __traceback__'i yok


# ── Cozum Islemi Testleri ─────────────────────────────────────


class TestCozumKaydetVeBul:
    """cozum_kaydet + cozum_bul entegrasyonu."""

    def test_kaydet_ve_bul(self):
        """Happy path: cozum kaydet, sonra bul."""
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
        """Happy path: basarisiz kayit cozum_bul'da donmez."""
        imza = "test_imza_basarisiz"
        cozum_kaydet(imza, "TypeError", "tip hatasi", "", "test.py", basarili=False)
        assert cozum_bul(imza) is None

    def test_gecersiz_imza_bul(self):
        """Error case: olmayan imza ile cozum_bul None doner."""
        assert cozum_bul("olmayan_imza_xyz_123") is None


# ── Yardimci Fonksiyon Testleri ───────────────────────────────


class TestYardimcilar:
    """ttl_temizle, istatistik, backoff_bekle."""

    def test_istatistik_sifir(self):
        """Happy path: hic kayit yokken istatistik 0 doner."""
        stats = istatistik()
        assert stats["toplam"] == 0
        assert stats["basarili"] == 0

    def test_backoff_bekle_usseldir(self):
        """Happy path: backoff suresi ussel artar."""
        b1 = backoff_bekle(1)
        b2 = backoff_bekle(2)
        b3 = backoff_bekle(3)
        assert b1 < b2 < b3
        assert b1 == 1.0
        assert b2 == 2.0
        assert b3 == 4.0

    def test_ttl_temizle_bos(self):
        """Happy path: bos DB'de ttl_temizle hata vermez."""
        silinen = ttl_temizle()
        assert silinen == 0


# ── Ogrenme Dongusu Testleri ──────────────────────────────────


class TestOgrenmeDongusu:
    """OgrenmeDongusu — ogren metodu."""

    def test_ogrenme_dongusu_baslatma(self):
        """Happy path: OgrenmeDongusu olustur ve istatistik al."""
        dongu = OgrenmeDongusu(max_deneme=2)
        stats = dongu.istatistik()
        assert stats["toplam_ogrenme"] == 0
        assert stats["basari_orani"] == 0
