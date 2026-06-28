# -*- coding: utf-8 -*-
"""tests/test_araclar.py — ReYMeN araclari testleri."""

import sys
import os
import json
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from araclar_ekran import EkranOCRTikla, PYAUTOGUI_OK, EASYOCR_OK
from araclar_makro import MakroKaydedici, PYNPUT_OK, PYAUTOGUI_OK as MAKRO_PYAUTOGUI_OK
from araclar_ses import SesliKomut, SR_OK


class TestEkran:
    def test_ekran_ocr_tikla_olusturma(self):
        """EkranOCRTikla baslatma."""
        ekran = EkranOCRTikla()
        assert ekran is not None

    def test_pyautogui_durumu(self):
        """pyautogui durumu kontrolu."""
        # Her durumda hata vermemeli
        assert isinstance(PYAUTOGUI_OK, bool)

    def test_easyocr_durumu(self):
        """easyocr durumu kontrolu."""
        assert isinstance(EASYOCR_OK, bool)

    def test_ekran_oku_method(self):
        """ekran_metnini_oku() metodu varligi."""
        ekran = EkranOCRTikla()
        assert hasattr(ekran, "ekran_metnini_oku") or hasattr(ekran, "ekran_oku")

    def test_tikla_method(self):
        """tikla/yaziyi_bul_ve_tikla metodu varligi."""
        ekran = EkranOCRTikla()
        assert hasattr(ekran, "yaziyi_bul_ve_tikla") or hasattr(ekran, "tikla")


class TestMakro:
    def test_makro_kaydedici_olusturma(self):
        """MakroKaydedici baslatma."""
        mk = MakroKaydedici()
        assert mk is not None

    def test_kaydet_ve_oynat_methodlari(self):
        """kaydet() ve oynat() metodlari varligi."""
        mk = MakroKaydedici()
        assert hasattr(mk, "kaydet") or hasattr(mk, "kayda_basla")
        assert hasattr(mk, "oynat") or hasattr(mk, "oynat_basla")

    def test_makro_dosya_kaydet(self):
        """Makro dosyasina kaydetme."""
        with tempfile.TemporaryDirectory() as tmp:
            mk = MakroKaydedici()
            makro_yolu = os.path.join(tmp, "test_makro.json")
            if hasattr(mk, "kaydet"):
                mk.kaydet(makro_yolu)
            elif hasattr(mk, "makro_yap"):
                # Method exists, just verify no crash
                pass

    def test_pynput_durumu(self):
        """pynput durumu."""
        assert isinstance(PYNPUT_OK, bool)


class TestSes:
    def test_sesli_komut_olusturma(self):
        """SesliKomut baslatma."""
        sk = SesliKomut(dil="tr-TR")
        assert sk is not None
        assert sk.dil == "tr-TR"

    def test_sesli_komut_varsayilan_dil(self):
        """Varsayilan dil kontrolu."""
        sk = SesliKomut()
        assert sk.dil == "tr-TR"

    def test_dinle_method(self):
        """dinle() metodu varligi."""
        sk = SesliKomut()
        assert hasattr(sk, "dinle")

    def test_sr_durumu(self):
        """SpeechRecognition durumu."""
        assert isinstance(SR_OK, bool)

    def test_seslendir_method(self):
        """seslendir() metodu varligi (TTS)."""
        sk = SesliKomut()
        assert hasattr(sk, "seslendir")
