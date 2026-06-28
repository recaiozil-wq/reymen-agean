# -*- coding: utf-8 -*-
"""tests/test_health_check.py — HealthChecker kapsamlı test."""

import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from collections import namedtuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from reymen.sistem.health_check import (
    HealthChecker,
    HealthDurum,
    saglik_kontrolu,
    hizli_kontrol,
)


class TestHealthDurum:
    """HealthDurum sabit değerleri."""

    def test_iyi(self):
        assert HealthDurum.IYI == "iyi"

    def test_uyari(self):
        assert HealthDurum.UYARI == "uyari"

    def test_kritik(self):
        assert HealthDurum.KRITIK == "kritik"

    def test_hata(self):
        assert HealthDurum.HATA == "hata"

    def test_dort_deger(self):
        values = {HealthDurum.IYI, HealthDurum.UYARI, HealthDurum.KRITIK, HealthDurum.HATA}
        assert len(values) == 4


class TestHealthCheckerInit:
    """Başlangıç durumu."""

    def test_varsayilan_baslangic(self):
        hc = HealthChecker()
        assert hc.rapor["durum"] == HealthDurum.IYI
        assert hc.rapor["sorunlar"] == []
        assert hc.sorunlar == []

    def test_custom_base_dir(self, tmp_path):
        hc = HealthChecker(base_dir=tmp_path)
        assert hc.base_dir == tmp_path

    def test_rapor_zaman_var(self):
        hc = HealthChecker()
        assert "zaman" in hc.rapor

    def test_rapor_kontroller_bos(self):
        hc = HealthChecker()
        assert hc.rapor["kontroller"] == {}

    def test_kritik_moduller_listesi(self):
        assert len(HealthChecker.KRITIK_MODULLER) > 0
        assert "reymen.sistem.config_loader" in HealthChecker.KRITIK_MODULLER


class TestSorunEkle:
    """_sorun_ekle() — durum hiyerarşisi."""

    def test_uyari_iyi_den_buyuk(self):
        hc = HealthChecker()
        hc._sorun_ekle(HealthDurum.UYARI, "test", "msg")
        assert hc.rapor["durum"] == HealthDurum.UYARI
        assert len(hc.sorunlar) == 1

    def test_kritik_uyari_den_buyuk(self):
        hc = HealthChecker()
        hc._sorun_ekle(HealthDurum.UYARI, "test", "msg1")
        hc._sorun_ekle(HealthDurum.KRITIK, "test", "msg2")
        assert hc.rapor["durum"] == HealthDurum.KRITIK

    def test_hata_her_seyden_buyuk(self):
        hc = HealthChecker()
        hc._sorun_ekle(HealthDurum.KRITIK, "test", "msg1")
        hc._sorun_ekle(HealthDurum.HATA, "test", "msg2")
        assert hc.rapor["durum"] == HealthDurum.HATA

    def test_sorun_icerik(self):
        hc = HealthChecker()
        hc._sorun_ekle(HealthDurum.UYARI, "disk", "dusuk")
        sorun = hc.sorunlar[0]
        assert sorun["seviye"] == HealthDurum.UYARI
        assert sorun["alan"] == "disk"
        assert sorun["mesaj"] == "dusuk"

    def test_uyariyi_uyariyle_ustune_yazmaz(self):
        hc = HealthChecker()
        hc._sorun_ekle(HealthDurum.UYARI, "test", "msg1")
        hc._sorun_ekle(HealthDurum.UYARI, "test", "msg2")
        assert hc.rapor["durum"] == HealthDurum.UYARI
        assert len(hc.sorunlar) == 2


class TestDiskKontrol:
    """disk_kontrol() — disk alanı kontrolü."""

    def test_normal_durum(self, tmp_path):
        hc = HealthChecker(base_dir=tmp_path)
        result = hc.disk_kontrol()
        assert "toplam_gb" in result
        assert "bos_gb" in result
        assert "kullanim_orani" in result
        assert result["kullanilabilir_gb"] > 0

    def test_rapor_kaydi(self, tmp_path):
        hc = HealthChecker(base_dir=tmp_path)
        hc.disk_kontrol()
        assert "disk" in hc.rapor["kontroller"]

    def test_kritik_esik_mock(self, tmp_path):
        hc = HealthChecker(base_dir=tmp_path)
        DiskUsage = namedtuple("DiskUsage", ["total", "used", "free"])
        # 0.3GB free → kritik
        fake = DiskUsage(total=100*1024**3, used=99.7*1024**3, free=0.3*1024**3)
        with patch("shutil.disk_usage", return_value=fake):
            result = hc.disk_kontrol()
        assert result["kullanilabilir_gb"] == 0.3
        kritikler = [s for s in hc.sorunlar if s["seviye"] == HealthDurum.KRITIK]
        assert len(kritikler) == 1

    def test_uyari_esik_mock(self, tmp_path):
        hc = HealthChecker(base_dir=tmp_path)
        DiskUsage = namedtuple("DiskUsage", ["total", "used", "free"])
        # 1.5GB free → uyari
        fake = DiskUsage(total=100*1024**3, used=98.5*1024**3, free=1.5*1024**3)
        with patch("shutil.disk_usage", return_value=fake):
            result = hc.disk_kontrol()
        uyari = [s for s in hc.sorunlar if s["seviye"] == HealthDurum.UYARI]
        assert len(uyari) == 1


class TestBellekKontrol:
    """bellek_kontrol() — bellek kontrolü."""

    def test_psutil_yolu(self):
        """psutil varsa bellek bilgisini döndürür."""
        hc = HealthChecker()
        mock_psutil = MagicMock()
        mock_mem = MagicMock()
        mock_mem.total = 8 * 1024**3
        mock_mem.available = 4 * 1024**3
        mock_mem.percent = 50.0
        mock_psutil.virtual_memory.return_value = mock_mem

        import builtins
        real_import = builtins.__import__
        def fake_import(name, *args, **kwargs):
            if name == "psutil":
                return mock_psutil
            return real_import(name, *args, **kwargs)

        with patch.object(builtins, "__import__", side_effect=fake_import):
            result = hc.bellek_kontrol()
        assert "toplam_mb" in result
        assert result["toplam_mb"] > 0

    def test_psutil_olmayan_ortam(self, tmp_path):
        hc = HealthChecker(base_dir=tmp_path)
        # psutil import hatası + /proc/meminfo yok → not mesajı
        result = hc.bellek_kontrol()
        # En azından bir sonuç dönmeli
        assert isinstance(result, dict)


class TestModulKontrolu:
    """modul_kontrolu() — modül yükleme."""

    def test_basari_sayisi(self):
        hc = HealthChecker()
        with patch("importlib.import_module"):
            result = hc.modul_kontrolu()
        assert result["basarili"] == len(HealthChecker.KRITIK_MODULLER)

    def test_import_hatasi(self):
        hc = HealthChecker()
        with patch("importlib.import_module", side_effect=ImportError("yok")):
            result = hc.modul_kontrolu()
        assert result["basarisiz"] == len(HealthChecker.KRITIK_MODULLER)
        uyari = [s for s in hc.sorunlar if s["alan"] == "modul"]
        assert len(uyari) == len(HealthChecker.KRITIK_MODULLER)

    def test_genel_hata(self):
        hc = HealthChecker()
        with patch("importlib.import_module", side_effect=RuntimeError("beklenmeyen")):
            result = hc.modul_kontrolu()
        assert result["basarisiz"] == len(HealthChecker.KRITIK_MODULLER)


class TestApiBaglantisi:
    """api_baglantisi() — API erişilebilirlik."""

    def test_basarisiz_api(self):
        hc = HealthChecker()
        with patch("urllib.request.urlopen", side_effect=Exception("timeout")):
            result = hc.api_baglantisi()
        for isim in HealthChecker.API_SAGLIK_URLS:
            assert result[isim]["durum"] == "hata"

    def test_basarisiz_url_error(self):
        hc = HealthChecker()
        import urllib.error
        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("yok")):
            result = hc.api_baglantisi()
        for isim in HealthChecker.API_SAGLIK_URLS:
            assert result[isim]["durum"] == "erisilemez"

    def test_api_rapor_kaydi(self):
        hc = HealthChecker()
        with patch("urllib.request.urlopen", side_effect=Exception("x")):
            hc.api_baglantisi()
        assert "api" in hc.rapor["kontroller"]


class TestDosyaSistemiKontrol:
    """dosya_sistemi_kontrol() — dizin varlığı."""

    def test_tum_var(self, tmp_path):
        hc = HealthChecker(base_dir=tmp_path)
        # reymen/sistem, reymen/guvenlik, reymen/hafiza dizinlerini oluştur
        for d in ["reymen/sistem", "reymen/guvenlik", "reymen/hafiza"]:
            (tmp_path / d).mkdir(parents=True, exist_ok=True)
        result = hc.dosya_sistemi_kontrol()
        assert all(v == "var" for v in result.values() if isinstance(v, str))

    def test_yok_dizinler(self, tmp_path):
        hc = HealthChecker(base_dir=tmp_path)
        result = hc.dosya_sistemi_kontrol()
        eksik = [k for k, v in result.items() if v == "yok" and k != "base_dir"]
        assert len(eksik) > 0


class TestTamKontrol:
    """tam_kontrol() — tüm kontrolleri çalıştır."""

    def test_tum_kontroller_calisiyor(self):
        hc = HealthChecker()
        DiskUsage = namedtuple("DiskUsage", ["total", "used", "free"])
        fake = DiskUsage(100*1024**3, 50*1024**3, 50*1024**3)
        with patch("shutil.disk_usage", return_value=fake), \
             patch("urllib.request.urlopen", side_effect=Exception("x")):
            rapor = hc.tam_kontrol()
        assert "disk" in rapor["kontroller"]
        assert "bellek" in rapor["kontroller"]
        assert "moduller" in rapor["kontroller"]
        assert "api" in rapor["kontroller"]
        assert "dosya_sistemi" in rapor["kontroller"]
        assert "toplam_sorun" in rapor
        assert "sorun_ozeti" in rapor

    def test_sorun_ozeti_sayilari(self):
        hc = HealthChecker()
        DiskUsage = namedtuple("DiskUsage", ["total", "used", "free"])
        fake = DiskUsage(100*1024**3, 50*1024**3, 50*1024**3)
        # API'ler erişilemez → uyari; moduller gercek import →.isSuccess
        with patch("shutil.disk_usage", return_value=fake), \
             patch("urllib.request.urlopen", side_effect=Exception("x")):
            rapor = hc.tam_kontrol()
        ozet = rapor["sorun_ozeti"]
        assert rapor["toplam_sorun"] > 0
        assert ozet["uyari"] >= 0
        assert "kritik" in ozet
        assert "hata" in ozet


class TestSaglikKontrolu:
    """saglik_kontrolu() — global fonksiyon."""

    def test_donus_tipi(self):
        rapor = saglik_kontrolu()
        assert isinstance(rapor, dict)
        assert "durum" in rapor
        assert "kontroller" in rapor

    def test_sorun_ozeti_var(self):
        rapor = saglik_kontrolu()
        assert "sorun_ozeti" in rapor
        assert "kritik" in rapor["sorun_ozeti"]


class TestHizliKontrol:
    """hizli_kontrol() — özet string."""

    def test_format(self):
        sonuc = hizli_kontrol()
        assert "[" in sonuc
        assert "sorun" in sonuc.lower() or "SORUN" in sonuc
        assert "kritik" in sonuc.lower() or "KRITIK" in sonuc


class TestRaporFormati:
    """Rapor dict yapısı."""

    def test_rapor_keys(self):
        hc = HealthChecker()
        rapor = hc.tam_kontrol()
        gerekli = {"zaman", "durum", "kontroller", "sorunlar", "toplam_sorun", "sorun_ozeti"}
        assert gerekli.issubset(set(rapor.keys()))
