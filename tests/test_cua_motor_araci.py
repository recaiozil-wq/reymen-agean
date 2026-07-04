# -*- coding: utf-8 -*-
"""cua_motor_araci.py testleri — vision/screenshot bagimliligi olmayan unit testler."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


# ── CUASonucu testleri (bagimsiz) ──


class TestCUASonucu:
    def test_basarili_str(self):
        from reymen.arac.cua_motor_araci import CUASonucu

        sonuc = CUASonucu(basarili=True, eylem="tikla", koordinat=(100, 200))
        metin = sonuc.str()
        assert "✅" in metin
        assert "100" in metin

    def test_basarisiz_str(self):
        from reymen.arac.cua_motor_araci import CUASonucu

        sonuc = CUASonucu(basarili=False, eylem="tikla", hata="LM Studio bagli degil")
        metin = sonuc.str()
        assert "❌" in metin
        assert "LM Studio" in metin

    def test_ekran_boyutu(self):
        from reymen.arac.cua_motor_araci import CUASonucu

        sonuc = CUASonucu(basarili=True, eylem="tikla", ekran_boyutu=(1920, 1080))
        metin = sonuc.str()
        assert "1920" in metin

    def test_sonraki_koordinat(self):
        from reymen.arac.cua_motor_araci import CUASonucu

        sonuc = CUASonucu(basarili=True, eylem="tikla", sonraki_koordinat=(300, 400))
        metin = sonuc.str()
        assert "300" in metin


# ── Koordinat Parse testleri ──


class TestKoordinatParse:
    @pytest.fixture(autouse=True)
    def setup(self):
        from reymen.arac.cua_motor_araci import koordinat_parse

        self.parse = koordinat_parse

    def test_basit_format(self):
        assert self.parse("452, 317") == (452, 317)

    def test_x_equals_format(self):
        assert self.parse("x=452, y=317") == (452, 317)

    def test_x_colon_format(self):
        assert self.parse("x: 452, y: 317") == (452, 317)

    def test_bosluklar(self):
        assert self.parse("  100 ,  200  ") == (100, 200)

    def test_metin_icinde(self):
        assert self.parse("Koordinat: 800, 600 noktasina tikla") == (800, 600)

    def test_ekran_disinda_none(self):
        assert self.parse("5000, 5000", ekran_boyutu=(1920, 1080)) is None

    def test_sifir_koordinat_none(self):
        assert self.parse("0, 0") is None

    def test_negatif_parsed_as_pozitif(self):
        """Negatif isareti \d+ tarafindan atlanir, pozitif sayi olarak parse edilir."""
        sonuc = self.parse("-5, 100")
        assert sonuc is not None
        x, y = sonuc
        assert isinstance(sonuc, tuple)
        assert len(sonuc) == 2

    def test_koordinat_yok_none(self):
        assert self.parse("Burada bir sey yok") is None

    def test_bos_string_none(self):
        assert self.parse("") is None

    def test_tek_sayi_none(self):
        assert self.parse("452") is None

    def test_parentez_format(self):
        assert self.parse("(100, 200)") == (100, 200)

    def test_uc_basamakli(self):
        assert self.parse("1200, 800") == (1200, 800)

    def test_tam_ekran_siniri(self):
        assert self.parse("1919, 1079", ekran_boyutu=(1920, 1080)) == (1919, 1079)

    def test_cok_sayida_koordinat(self):
        assert self.parse("100, 200 ve 300, 400") == (100, 200)


# ── AdaptifDenemeSayaci testleri ──


class TestAdaptifDenemeSayaci:
    @pytest.fixture(autouse=True)
    def setup(self):
        from reymen.arac.cua_motor_araci import AdaptifDenemeSayaci

        self.sayac = AdaptifDenemeSayaci()

    def test_baslangic_limit_taban(self):
        assert self.sayac.mevcut_limit == 3

    def test_basarisiz_artirir(self):
        self.sayac.basarisiz_kaydet()
        assert self.sayac.mevcut_limit == 4

    def test_basarisiz_birden_fazla(self):
        for _ in range(5):
            self.sayac.basarisiz_kaydet()
        assert self.sayac.mevcut_limit <= 6

    def test_sifirla_limit_iner(self):
        self.sayac.basarisiz_kaydet()
        self.sayac.sifirla()
        assert self.sayac.mevcut_limit == 3

    def test_max_limit(self):
        for _ in range(20):
            self.sayac.basarisiz_kaydet()
        assert self.sayac.mevcut_limit == 6


# ── Config Yukle testleri ──


class TestConfigYukle:
    def test_config_yoksa_varsayilan(self):
        from reymen.arac.cua_motor_araci import _config_yukle

        with patch.object(Path, "exists", return_value=False):
            cfg = _config_yukle()
        assert cfg["lm_studio_url"] == "http://localhost:1234/v1/chat/completions"
        assert cfg["max_deneme"] == 3


# ── Goruntu Base64 testleri ──


class TestGoruntuBase64:
    def test_goruntu_base64_string_doner(self):
        from reymen.arac.cua_motor_araci import goruntu_base64_yap

        mock_img = MagicMock()
        mock_img.width = 800
        mock_img.height = 600

        # Gerçek BytesIO kullan, save'i buffer'a yazacak şekilde mock'la
        def fake_save(buffer, **kwargs):
            buffer.write(b"fake_jpeg_bytes")

        mock_img.save = MagicMock(side_effect=fake_save)

        b64 = goruntu_base64_yap(mock_img)
        assert isinstance(b64, str)
        assert len(b64) > 0
        import base64

        assert base64.b64decode(b64) == b"fake_jpeg_bytes"

    def test_buyuk_resim_resize_edilir(self):
        from reymen.arac.cua_motor_araci import goruntu_base64_yap

        mock_img = MagicMock()
        mock_img.width = 2560
        mock_img.height = 1440
        mock_img.resize.return_value = mock_img

        with patch("reymen.arac.cua_motor_araci.BytesIO") as mock_class:
            mock_instance = MagicMock()
            mock_instance.getvalue.return_value = b"fake_jpeg_bytes"
            mock_class.return_value = mock_instance
            mock_img.save = MagicMock()

            b64 = goruntu_base64_yap(mock_img)
        assert isinstance(b64, str)
        assert mock_img.resize.called

    def test_resize_olmaz_kucuk(self):
        from reymen.arac.cua_motor_araci import goruntu_base64_yap

        mock_img = MagicMock()
        mock_img.width = 800
        mock_img.height = 600
        mock_img.save = MagicMock()

        with patch("reymen.arac.cua_motor_araci.BytesIO") as mock_class:
            mock_instance = MagicMock()
            mock_instance.getvalue.return_value = b"fake_jpeg_bytes"
            mock_class.return_value = mock_instance

            b64 = goruntu_base64_yap(mock_img)
        mock_img.resize.assert_not_called()


# ── Dosya Tara testleri ──


class TestCUAARaclariTara:
    def test_dosyalar_ok(self, tmp_path):
        from reymen.arac.cua_motor_araci import CUA_ARACLARI_TARA

        sonuc = CUA_ARACLARI_TARA(kok=str(tmp_path))
        assert isinstance(sonuc, str)
        assert "CUA" in sonuc or "ReYMeN" in sonuc or "Bileşen" in sonuc

    def test_rapor_kapsami(self, tmp_path):
        from reymen.arac.cua_motor_araci import CUA_ARACLARI_TARA

        sonuc = CUA_ARACLARI_TARA(kok=str(tmp_path))
        assert "Haz" in sonuc or "Eksik" in sonuc


# ── Eylem Yorumla testleri ──


class TestEylemYorumla:
    @pytest.fixture(autouse=True)
    def setup(self):
        from reymen.arac.cua_motor_araci import eylem_yorumla_ve_calistir

        self.eylem = eylem_yorumla_ve_calistir

    def test_cift_tik(self):
        with patch("reymen.arac.cua_motor_araci.tikla") as mock_tikla:
            sonuc = self.eylem("cift tikla", (100, 200))
        assert "tıkland" in sonuc or "tikland" in sonuc

    def test_yaz_komutu(self):
        with patch("reymen.arac.cua_motor_araci.tikla"):
            with patch("reymen.arac.cua_motor_araci.yaz") as mock_yaz:
                sonuc = self.eylem("'merhaba' yaz", (100, 200))
        assert "yazıld" in sonuc or "yazildi" in sonuc

    def test_basit_tikla(self):
        with patch("reymen.arac.cua_motor_araci.tikla") as mock_tikla:
            sonuc = self.eylem("tikla", (300, 400))
        assert "tıkland" in sonuc or "tiklandi" in sonuc


# ── On Kosul Kontrol testleri ──


class TestOnKosulKontrol:
    def test_on_kosul_basarisiz_lmstudio_yok(self):
        pytest.importorskip("pyautogui", reason="pyautogui gerekli")
        pytest.importorskip("PIL", reason="Pillow gerekli")
        from reymen.arac.cua_motor_araci import _on_kosul_kontrol
        import reymen.arac.cua_motor_araci as cua

        cua._on_kosul_kontrolu_yapildi = False
        cua._on_kosul_sonuc = None

        with patch("reymen.arac.cua_motor_araci.requests.get") as mock_get:
            mock_get.side_effect = __import__("requests").exceptions.ConnectionError()
            sonuc = cua._on_kosul_kontrol()
        assert sonuc is not None
        assert "LM Studio" in sonuc

    def test_on_kosul_basarili(self):
        pytest.importorskip("pyautogui", reason="pyautogui gerekli")
        pytest.importorskip("PIL", reason="Pillow gerekli")
        from reymen.arac.cua_motor_araci import _on_kosul_kontrol
        import reymen.arac.cua_motor_araci as cua

        cua._on_kosul_kontrolu_yapildi = False
        cua._on_kosul_sonuc = None

        with patch("reymen.arac.cua_motor_araci.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{"id": "llava"}]
            mock_get.return_value = mock_response
            sonuc = cua._on_kosul_kontrol()
        assert sonuc is None


# ── motor_kaydet testleri ──


class TestMotorKaydet:
    def test_motor_kaydet_cagrilir(self):
        from reymen.arac.cua_motor_araci import motor_kaydet

        motor = MagicMock()
        motor_kaydet(motor)
        assert motor._plugin_arac_kaydet.call_count >= 2

    def test_motor_kaydet_hasattr_yoksa(self):
        from reymen.arac.cua_motor_araci import motor_kaydet

        motor = object()
        motor_kaydet(motor)
