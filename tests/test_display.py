# -*- coding: utf-8 -*-
"""display.py birim testleri."""

import sys
from pathlib import Path

# Proje kokunu ekle
PROJ_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJ_ROOT))

import pytest
from display import Display, _ANSI


class TestDisplayRenkliYaz:
    """Display.renkli_yaz() testleri."""

    def test_renkli_yaz_varsayilan(self, capsys):
        d = Display()
        d.renkli_yaz("test mesaji")
        captured = capsys.readouterr()
        assert captured.out == "test mesaji\n"

    def test_renkli_yaz_yesil(self, capsys):
        d = Display()
        d.renkli_yaz("yesil yazi", renk="yesil")
        captured = capsys.readouterr()
        assert _ANSI["yesil"] in captured.out
        assert "yesil yazi" in captured.out
        assert _ANSI["sifirla"] in captured.out

    def test_renkli_yaz_kalin(self, capsys):
        d = Display()
        d.renkli_yaz("kalin yazi", kalin=True)
        captured = capsys.readouterr()
        assert _ANSI["kalin"] in captured.out

    def test_renkli_yaz_kalin_yesil(self, capsys):
        d = Display()
        d.renkli_yaz("kalin yesil", renk="yesil", kalin=True)
        captured = capsys.readouterr()
        assert _ANSI["kalin"] in captured.out
        assert _ANSI["yesil"] in captured.out

    def test_renkli_yaz_gecersiz_renk(self, capsys):
        d = Display()
        d.renkli_yaz("default", renk="yok")
        captured = capsys.readouterr()
        assert captured.out == "default\n"

    def test_renkli_yaz_son_parametre(self, capsys):
        d = Display()
        d.renkli_yaz("bosluk", son=" ")
        captured = capsys.readouterr()
        assert captured.out == "bosluk "

    def test_renkli_yaz_tum_renkler(self, capsys):
        d = Display()
        for renk in ["kirmizi", "yesil", "sari", "mavi", "magenta", "cyan", "beyaz"]:
            d.renkli_yaz(renk, renk=renk)
        captured = capsys.readouterr()
        for renk in ["kirmizi", "yesil", "sari", "mavi", "magenta", "cyan", "beyaz"]:
            assert renk in captured.out
            assert _ANSI[renk] in captured.out


class TestDisplayTablo:
    """Display.tablo() testleri."""

    def test_tablo_bos_baslik(self, capsys):
        d = Display()
        d.tablo([], [])
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_tablo_tek_satir(self, capsys):
        d = Display()
        d.tablo(["Ad"], [["Ali"]])
        captured = capsys.readouterr()
        assert "Ad" in captured.out
        assert "Ali" in captured.out
        assert "+" in captured.out

    def test_tablo_cok_satir(self, capsys):
        d = Display()
        d.tablo(["Ad", "Yas"], [["Ali", "30"], ["Ayse", "25"]])
        captured = capsys.readouterr()
        assert "Ad" in captured.out
        assert "Yas" in captured.out
        assert "Ali" in captured.out
        assert "Ayse" in captured.out
        assert "30" in captured.out
        assert "25" in captured.out

    def test_tablo_sinirsiz(self, capsys):
        d = Display()
        d.tablo(["X"], [["1"]], sinir=False)
        captured = capsys.readouterr()
        # Her '+' cizgi satirinda 2 adet '+' bulunur (acilis ve kapanis)
        # sinir=False: ust cizgi (2x+) + baslik alti cizgi (2x+) = 4
        # Alt cizgi olmamali — yani sinir=True'dan 2 az olmali
        cizgi_sayisi = captured.out.count("+")
        # sinir=True olsaydi 6 olurdu; sinir=False ile 4 olmali
        assert cizgi_sayisi == 4

    def test_tablo_genislik_hesabi(self, capsys):
        d = Display()
        d.tablo(["A"], [["uzun_metin"], ["kisa"]])
        captured = capsys.readouterr()
        assert "uzun_metin" in captured.out
        assert "kisa" in captured.out


class TestDisplayProgressBar:
    """Display.progress_bar() testleri."""

    def test_progress_baslangic(self, capsys):
        d = Display()
        d.progress_bar(0, 10, baslik="Test")
        captured = capsys.readouterr()
        assert "Test" in captured.out
        assert "%" in captured.out

    def test_progress_tamam(self, capsys):
        d = Display()
        d.progress_bar(10, 10, baslik="Bitti")
        captured = capsys.readouterr()
        assert "100%" in captured.out

    def test_progress_yarida(self, capsys):
        d = Display()
        d.progress_bar(5, 10, baslik="Yarida")
        captured = capsys.readouterr()
        assert "Yarida" in captured.out

    def test_progress_toplam_sifir(self, capsys):
        d = Display()
        d.progress_bar(0, 0)
        captured = capsys.readouterr()
        assert "0%" in captured.out

    def test_progress_genislik_parametresi(self, capsys):
        d = Display()
        d.progress_bar(5, 10, genislik=20)
        captured = capsys.readouterr()
        assert "%" in captured.out
        # 20 karakter genislik icin bar olusmali
        assert "[" in captured.out


class TestDisplayEntegrasyon:
    """Display entegrasyon testleri."""

    def test_display_ornek_main(self, capsys):
        """__main__ blogundaki gibi kullanim."""
        d = Display()
        d.renkli_yaz("Merhaba Dunya!", renk="yesil")
        d.renkli_yaz("Hata!", renk="kirmizi")
        d.tablo(["Ad", "Yas"], [["Ali", "30"], ["Ayse", "25"]])
        d.progress_bar(5, 10, baslik="Ilerleme")
        d.progress_bar(10, 10, baslik="Tamamlandi")
        captured = capsys.readouterr()
        assert "Merhaba Dunya!" in captured.out
        assert "Hata!" in captured.out
        assert "Ali" in captured.out
        assert "Ilerleme" in captured.out
        assert "Tamamlandi" in captured.out
