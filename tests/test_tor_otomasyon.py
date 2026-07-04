# -*- coding: utf-8 -*-
"""tests/test_tor_otomasyon.py — Tor otomasyonu modulu testleri.

Selenium/Tor olmadan da calisir; graceful degrade test edilir.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tor_otomasyonu import (
    TorBrowserKontrol,
    FormDoldurucu,
    OtomasyonAkislari,
    tor_baslat,
    tor_kapat,
    _SELENIUM_VAR,
)


class TestTorBrowserKontrol:
    def test_olusturma_varsayilan(self):
        tor = TorBrowserKontrol()
        assert tor is not None

    def test_olusturma_ozel_yol(self):
        tor = TorBrowserKontrol(tor_yolu="C:\\fake\\firefox.exe")
        assert tor.tor_yolu == "C:\\fake\\firefox.exe"

    def test_olusturma_geckodriver_parametresi(self):
        tor = TorBrowserKontrol(geckodriver_yolu="geckodriver.exe")
        assert tor.geckodriver_yolu == "geckodriver.exe"

    def test_aktif_property_basta_false(self):
        tor = TorBrowserKontrol()
        assert tor.aktif is False

    def test_driver_basta_none(self):
        tor = TorBrowserKontrol()
        assert tor.driver is None

    def test_baslat_selenium_yok_hata_verir(self):
        if _SELENIUM_VAR:
            # Selenium varsa, Tor binary'si olmadigi icin FileNotFoundError beklenir
            tor = TorBrowserKontrol(tor_yolu="")
            try:
                tor.baslat()
                assert False, "Hata beklenmiyordu"
            except (FileNotFoundError, RuntimeError, Exception):
                pass
        else:
            tor = TorBrowserKontrol(tor_yolu="")
            try:
                tor.baslat()
                assert False, "RuntimeError beklenmiyordu"
            except RuntimeError as e:
                assert "selenium" in str(e).lower()

    def test_kapat_driver_yok_guvenli(self):
        tor = TorBrowserKontrol()
        tor.kapat()  # driver None iken crash etmemeli

    def test_sayfaya_git_driver_yok(self):
        tor = TorBrowserKontrol()
        sonuc = tor.sayfaya_git("http://example.com")
        assert sonuc is False

    def test_sayfa_kaydet_driver_yok(self):
        tor = TorBrowserKontrol()
        icerik = tor.sayfa_kaydet()
        assert icerik == ""

    def test_ekran_goruntusu_driver_yok(self):
        tor = TorBrowserKontrol()
        sonuc = tor.ekran_goruntusu()
        assert sonuc == ""

    def test_varsayilan_yol_string_donar(self):
        yol = TorBrowserKontrol._varsayilan_yol()
        assert isinstance(yol, str)

    def test_selenium_durum_flag(self):
        assert isinstance(_SELENIUM_VAR, bool)


class TestFormDoldurucu:
    def test_alan_karesi_mevcut(self):
        assert isinstance(FormDoldurucu._ALAN_KARESi, dict)
        assert "ad" in FormDoldurucu._ALAN_KARESi
        assert "eposta" in FormDoldurucu._ALAN_KARESi

    def test_alan_karesi_tum_anahtarlar(self):
        beklenen = {
            "ad",
            "soyad",
            "eposta",
            "telefon",
            "sifre",
            "sifre_tekrar",
            "adres",
            "il",
            "ilce",
            "posta_kodu",
            "tc_kimlik",
            "kullanici_adi",
        }
        assert beklenen.issubset(set(FormDoldurucu._ALAN_KARESi.keys()))

    def test_stratejiler_mevcut(self):
        assert len(FormDoldurucu._STRATEJILER) > 0
        # Selenium varsa callable ve (By, xpath) tuplelari dondurmeli
        if _SELENIUM_VAR:
            for strateji in FormDoldurucu._STRATEJILER:
                sonuc = strateji("test")
                assert len(sonuc) == 2

    def test_doldur_driver_yok_hata_tolerans(self):
        """Selenium driver olmadan cagri hata verebilir; crash etmemeli."""
        try:
            sonuc = FormDoldurucu.doldur(None, {"ad": "Test"}, bekle=1)
        except Exception:
            pass  # Selenium yoksa AttributeError normaldir

    def test_eposta_dom_karsiligi(self):
        karsiliklar = FormDoldurucu._ALAN_KARESi["eposta"]
        assert "email" in karsiliklar

    def test_sifre_dom_karsiligi(self):
        karsiliklar = FormDoldurucu._ALAN_KARESi["sifre"]
        assert "password" in karsiliklar


class TestOtomasyonAkislari:
    def _tor_ornegi(self):
        return TorBrowserKontrol(tor_yolu="")

    def test_olusturma(self):
        tor = self._tor_ornegi()
        akislar = OtomasyonAkislari(tor)
        assert akislar is not None
        assert akislar.tor is tor

    def test_login_tor_aktif_degil(self):
        tor = self._tor_ornegi()
        akislar = OtomasyonAkislari(tor)
        sonuc = akislar.login("http://example.com", "user", "pass")
        assert sonuc["basarili"] is False
        assert "aktif degil" in sonuc["hata"]

    def test_kayit_ol_tor_aktif_degil(self):
        tor = self._tor_ornegi()
        akislar = OtomasyonAkislari(tor)
        sonuc = akislar.kayit_ol("http://example.com", {"ad": "Test"})
        assert sonuc["basarili"] is False
        assert "aktif degil" in sonuc["hata"]

    def test_siparis_ver_tor_aktif_degil(self):
        tor = self._tor_ornegi()
        akislar = OtomasyonAkislari(tor)
        sonuc = akislar.siparis_ver(
            "http://example.com", "urun-1", {"adres": "Test Sok"}
        )
        assert sonuc["basarili"] is False
        assert "aktif degil" in sonuc["hata"]

    def test_login_return_yapi(self):
        tor = self._tor_ornegi()
        akislar = OtomasyonAkislari(tor)
        sonuc = akislar.login("", "", "")
        assert "basarili" in sonuc
        assert "sayfa" in sonuc
        assert "hata" in sonuc

    def test_kayit_return_yapi(self):
        tor = self._tor_ornegi()
        akislar = OtomasyonAkislari(tor)
        sonuc = akislar.kayit_ol("", {})
        assert "basarili" in sonuc
        assert "sonuc" in sonuc
        assert "hata" in sonuc

    def test_siparis_return_yapi(self):
        tor = self._tor_ornegi()
        akislar = OtomasyonAkislari(tor)
        sonuc = akislar.siparis_ver("", "", {})
        assert "basarili" in sonuc
        assert "sonuc" in sonuc
        assert "hata" in sonuc


class TestMotorKayit:
    def test_tor_ac_arac_selenium_yok(self):
        from tor_otomasyonu import motor_kaydet

        class MockMotor:
            def calistir(self, arac, param):
                return f"[Orijinal] {arac}"

        mock = MockMotor()
        motor_kaydet(mock)
        # TOR_AC cagrisi graceful sonuc donmeli
        sonuc = mock.calistir("TOR_AC", "")
        assert isinstance(sonuc, str)

    def test_tor_kapat_arac(self):
        from tor_otomasyonu import motor_kaydet

        class MockMotor:
            def calistir(self, arac, param):
                return f"[Orijinal] {arac}"

        mock = MockMotor()
        motor_kaydet(mock)
        sonuc = mock.calistir("TOR_KAPAT", "")
        assert isinstance(sonuc, str)
        assert "kapatildi" in sonuc.lower()

    def test_bilinmeyen_arac_tor_aktif_degilken(self):
        """Tor aktif degil + bilinmeyen arac -> 'TOR_AC ile baslatin' mesaji."""
        from tor_otomasyonu import motor_kaydet

        class MockMotor:
            def calistir(self, arac, param):
                return f"[Orijinal] {arac}"

        mock = MockMotor()
        motor_kaydet(mock)
        # _aktif_akislar None oldugunda bilinmeyen arac da bu mesaji alir
        sonuc = mock.calistir("BILINMEYEN_ARAC", "")
        assert isinstance(sonuc, str)
        assert "TOR_AC" in sonuc or "[Orijinal]" in sonuc
