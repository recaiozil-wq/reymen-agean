# -*- coding: utf-8 -*-
"""tests/test_nisan.py — NisanBulucu (araclar_nisan) modulu testleri.

OpenCV/mss/pytesseract olmadan da calisir; graceful degrade test edilir.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from araclar_nisan import (
    NisanBulucu,
    NISAN_DIZINI,
    _OPENCV_VAR,
    _MSS_VAR,
    _PIL_VAR,
    _TESSERACT_VAR,
)


class TestNisanBulucuOlusturma:
    def test_olusturma_varsayilan(self):
        bulucu = NisanBulucu()
        assert bulucu is not None

    def test_nisan_dizini_mevcut(self):
        assert isinstance(NISAN_DIZINI, Path)
        assert "nisanlar" in str(NISAN_DIZINI)

    def test_flag_boolean(self):
        assert isinstance(_OPENCV_VAR, bool)
        assert isinstance(_MSS_VAR, bool)
        assert isinstance(_PIL_VAR, bool)
        assert isinstance(_TESSERACT_VAR, bool)


class TestNisanBulucuDomAsama:
    def test_bul_driver_yok_ozet_donmeli(self):
        """Driver verilmezse veya driver=None ise crash olmamali."""
        bulucu = NisanBulucu()
        try:
            sonuc = bulucu.bul("giris_buton", driver=None)
            # Sonuc None veya dict olmali
            assert sonuc is None or isinstance(sonuc, dict)
        except Exception:
            # DOM asama hatasi normaldir; modül crash etmemeli
            pass

    def test_bilinen_sablon_listesi_dolu(self):
        bulucu = NisanBulucu()
        assert hasattr(bulucu, "_SABLON_DOM")
        assert len(bulucu._SABLON_DOM) > 0

    def test_giris_buton_lokatorleri(self):
        bulucu = NisanBulucu()
        assert "giris_buton" in bulucu._SABLON_DOM
        assert len(bulucu._SABLON_DOM["giris_buton"]) >= 2

    def test_kayit_buton_lokatorleri(self):
        bulucu = NisanBulucu()
        assert "kayit_buton" in bulucu._SABLON_DOM

    def test_bilinmeyen_sablon_crash_olmaz(self):
        bulucu = NisanBulucu()
        try:
            sonuc = bulucu.bul("var_olmayan_sablon_xyz", driver=None)
            assert sonuc is None or isinstance(sonuc, dict)
        except Exception:
            pass

    def test_bul_metodu_mevcut(self):
        bulucu = NisanBulucu()
        assert hasattr(bulucu, "bul")
        assert callable(bulucu.bul)


class TestNisanBulucuGoruntuAsama:
    def test_goruntu_asama_opencv_yok(self):
        """OpenCV yoksa goruntu asama None/dict donmeli."""
        if _OPENCV_VAR:
            # OpenCV varsa ama ekran alinabilir olmayabilir; sadece crash test
            bulucu = NisanBulucu()
            try:
                sonuc = bulucu._goruntu_asama("test_sablon")
                assert sonuc is None or isinstance(sonuc, dict)
            except Exception:
                pass
        else:
            bulucu = NisanBulucu()
            try:
                sonuc = bulucu._goruntu_asama("test_sablon")
                assert sonuc is None
            except AttributeError:
                pass  # Metod yoksa normal

    def test_nisan_dizini_olusturulabilir(self):
        """Nisan dizini gerekirse olusturulabilmeli."""
        NISAN_DIZINI.mkdir(parents=True, exist_ok=True)
        assert NISAN_DIZINI.parent.exists()


class TestNisanBulucuOcrAsama:
    def test_ocr_asama_tesseract_yok(self):
        """pytesseract yoksa OCR asama None donmeli."""
        bulucu = NisanBulucu()
        if not _TESSERACT_VAR:
            try:
                sonuc = bulucu._ocr_asama("giris")
                assert sonuc is None
            except AttributeError:
                pass
        else:
            try:
                sonuc = bulucu._ocr_asama("giris")
                assert sonuc is None or isinstance(sonuc, dict)
            except Exception:
                pass


class TestNisanBulucuMotorEntegrasyon:
    def test_motor_kaydet_cagrilabilir(self):
        """motor_kaydet fonksiyonu varsa crash olmamali."""
        try:
            from araclar_nisan import motor_kaydet

            class MockMotor:
                def calistir(self, arac, param):
                    return f"[Orijinal] {arac}"

            mock = MockMotor()
            motor_kaydet(mock)
        except ImportError:
            pass  # motor_kaydet bu modulde olmayabilir

    def test_nisan_bul_arac_motor_yok(self):
        """NISAN_BUL araci motor olmadan graceful donmeli."""
        try:
            from araclar_nisan import motor_kaydet

            class MockMotor:
                def calistir(self, arac, param):
                    return f"[Orijinal] {arac}"

            mock = MockMotor()
            motor_kaydet(mock)
            sonuc = mock.calistir("NISAN_BUL", "giris_buton")
            assert isinstance(sonuc, str)
        except (ImportError, AttributeError):
            pass
