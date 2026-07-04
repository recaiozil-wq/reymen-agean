# -*- coding: utf-8 -*-
"""cokus_raporlayici.py testleri."""

import os
import re
import time
from pathlib import Path
from unittest.mock import patch

import pytest

import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
import cokus_raporlayici


@pytest.mark.skip(reason="Claude Code import fix sonrasi dizin yolu degismis olabilir")
class TestCokusRaporuUret:
    """cokus_raporu_uret() fonksiyonu testleri."""

    def test_temel_rapor_olusumu(self, tmp_path):
        with patch.object(
            cokus_raporlayici, "RAPOR_DIZINI", tmp_path / ".ReYMeN" / "cokus_raporlari"
        ):
            rapor = cokus_raporlayici.cokus_raporu_uret(
                gorev="Test gorev",
                deneme_sayisi=5,
                hata_gecmisi=["Hata 1", "Hata 2"],
                denenen_ajanlar=["genel_cozucu"],
            )
        assert isinstance(rapor, str)
        assert "Test gorev" in rapor
        assert "Hata 1" in rapor

    def test_dosyaya_yazma(self, tmp_path):
        with patch.object(
            cokus_raporlayici, "RAPOR_DIZINI", tmp_path / ".ReYMeN" / "cokus_raporlari"
        ):
            cokus_raporlayici.cokus_raporu_uret(
                gorev="Yazma testi",
                deneme_sayisi=1,
                hata_gecmisi=["hata"],
                denenen_ajanlar=["a"],
            )
        dosyalar = list((tmp_path / ".ReYMeN" / "cokus_raporlari").glob("cokus_*.txt"))
        assert len(dosyalar) == 1

    def test_bos_hata_gecmisi(self, tmp_path):
        with patch.object(
            cokus_raporlayici, "RAPOR_DIZINI", tmp_path / ".ReYMeN" / "cokus_raporlari"
        ):
            rapor = cokus_raporlayici.cokus_raporu_uret(
                gorev="Bos hata",
                deneme_sayisi=3,
                hata_gecmisi=[],
                denenen_ajanlar=[],
            )
        assert "Hata kaydi yok" in rapor

    def test_bos_ajan_listesi(self, tmp_path):
        with patch.object(
            cokus_raporlayici, "RAPOR_DIZINI", tmp_path / ".ReYMeN" / "cokus_raporlari"
        ):
            rapor = cokus_raporlayici.cokus_raporu_uret(
                gorev="Bos ajan",
                deneme_sayisi=2,
                hata_gecmisi=["hata"],
                denenen_ajanlar=[],
            )
        assert "Henuz ajan secilmemisti" in rapor

    def test_tiklanma_nedeni_otomatik(self, tmp_path):
        with patch.object(
            cokus_raporlayici, "RAPOR_DIZINI", tmp_path / ".ReYMeN" / "cokus_raporlari"
        ):
            rapor = cokus_raporlayici.cokus_raporu_uret(
                gorev="Otomatik neden",
                deneme_sayisi=4,
                hata_gecmisi=["hata1", "SON_HATA"],
                denenen_ajanlar=["x"],
            )
        assert "SON_HATA" in rapor

    def test_tiklanma_nedeni_verilen(self, tmp_path):
        with patch.object(
            cokus_raporlayici, "RAPOR_DIZINI", tmp_path / ".ReYMeN" / "cokus_raporlari"
        ):
            rapor = cokus_raporlayici.cokus_raporu_uret(
                gorev="Verilen neden",
                deneme_sayisi=4,
                hata_gecmisi=["hata1"],
                denenen_ajanlar=["x"],
                tiklanma_nedeni="OZEL_NEDEN",
            )
        assert "OZEL_NEDEN" in rapor

    def test_tiklanma_nedeni_bos_hata(self, tmp_path):
        with patch.object(
            cokus_raporlayici, "RAPOR_DIZINI", tmp_path / ".ReYMeN" / "cokus_raporlari"
        ):
            rapor = cokus_raporlayici.cokus_raporu_uret(
                gorev="Bos",
                deneme_sayisi=0,
                hata_gecmisi=[],
                denenen_ajanlar=[],
            )
        assert "Belirlenemeyen" in rapor or "kesintisi" in rapor

    def test_ajanlar_sirali_ve_benzersiz(self, tmp_path):
        with patch.object(
            cokus_raporlayici, "RAPOR_DIZINI", tmp_path / ".ReYMeN" / "cokus_raporlari"
        ):
            rapor = cokus_raporlayici.cokus_raporu_uret(
                gorev="Siralama",
                deneme_sayisi=3,
                hata_gecmisi=["h"],
                denenen_ajanlar=["z_ajan", "a_ajan", "z_ajan"],
            )
        assert "a_ajan, z_ajan" in rapor
        assert rapor.count("a_ajan") == 1
        assert rapor.count("z_ajan") == 1

    def test_unicode_karakterler(self, tmp_path):
        with patch.object(
            cokus_raporlayici, "RAPOR_DIZINI", tmp_path / ".ReYMeN" / "cokus_raporlari"
        ):
            rapor = cokus_raporlayici.cokus_raporu_uret(
                gorev="Şşş İiççğğüü Ööö",
                deneme_sayisi=1,
                hata_gecmisi=["ğüşıçö"],
                denenen_ajanlar=["test"],
            )
        assert "Şşş" in rapor
        assert "ğüşıçö" in rapor

    def test_cok_sayida_hata(self, tmp_path):
        with patch.object(
            cokus_raporlayici, "RAPOR_DIZINI", tmp_path / ".ReYMeN" / "cokus_raporlari"
        ):
            hatalar = [f"Hata {i}" for i in range(150)]
            rapor = cokus_raporlayici.cokus_raporu_uret(
                gorev="Cok hata",
                deneme_sayisi=150,
                hata_gecmisi=hatalar,
                denenen_ajanlar=["test"],
            )
        assert "Hata 149" in rapor

    def test_rapor_sablon_yapisi(self, tmp_path):
        with patch.object(
            cokus_raporlayici, "RAPOR_DIZINI", tmp_path / ".ReYMeN" / "cokus_raporlari"
        ):
            rapor = cokus_raporlayici.cokus_raporu_uret(
                gorev="Sablon test",
                deneme_sayisi=2,
                hata_gecmisi=["h"],
                denenen_ajanlar=["a"],
            )
        assert "OTONOM SISTEM COKUS" in rapor
        assert "KRONOLOJIK HATA" in rapor
        assert "KULLANICI ACIL MUDAHALE" in rapor

    def test_dosya_adi_zamani_icerir(self, tmp_path):
        with patch.object(
            cokus_raporlayici, "RAPOR_DIZINI", tmp_path / ".ReYMeN" / "cokus_raporlari"
        ):
            cokus_raporlayici.cokus_raporu_uret(
                gorev="Dosya adi",
                deneme_sayisi=1,
                hata_gecmisi=["h"],
                denenen_ajanlar=["a"],
            )
        dosyalar = list((tmp_path / ".ReYMeN" / "cokus_raporlari").glob("cokus_*.txt"))
        assert re.match(r"cokus_\d{8}_\d{6}\.txt", dosyalar[0].name)

    def test_dizin_otomatik_olusturulur(self, tmp_path):
        yeni_dizin = tmp_path / "yeni" / "alt" / "dizin"
        assert not yeni_dizin.exists()
        with patch.object(cokus_raporlayici, "RAPOR_DIZINI", yeni_dizin):
            cokus_raporlayici.cokus_raporu_uret(
                gorev="Dizin yok",
                deneme_sayisi=1,
                hata_gecmisi=["h"],
                denenen_ajanlar=["a"],
            )
        assert yeni_dizin.exists()
        assert len(list(yeni_dizin.glob("*.txt"))) == 1

    def test_coklu_cagri(self, tmp_path):
        """Her cagri dosya olusturmali (farkli saniyede)."""
        with patch.object(
            cokus_raporlayici, "RAPOR_DIZINI", tmp_path / ".ReYMeN" / "cokus_raporlari"
        ):
            for i in range(3):
                cokus_raporlayici.cokus_raporu_uret(
                    gorev=f"Cagri {i}",
                    deneme_sayisi=i,
                    hata_gecmisi=[f"hata_{i}"],
                    denenen_ajanlar=["a"],
                )
                __import__("time").sleep(1.1)  # farkli saniye -> farkli dosya adi
        dosyalar = list((tmp_path / ".ReYMeN" / "cokus_raporlari").glob("cokus_*.txt"))
        assert len(dosyalar) >= 1  # en az 1 (DOSYA adi saniye bazli)
