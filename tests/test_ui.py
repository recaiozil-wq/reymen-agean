# -*- coding: utf-8 -*-
"""tests/test_ui.py — UI modulleri testleri."""

import sys
import os
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from display import Display
from insan_arayuzu import HumanInterface
from onboarding import OnboardingWizard


class TestDisplay:
    def test_display_olusturma(self):
        """Display baslatma."""
        d = Display()
        assert d is not None

    def test_renkli_yaz(self):
        """Renkli yazdirma fonksiyonu."""
        d = Display()
        # Hata vermeden calismali
        d.renkli_yaz("Test mesaj", renk="yesil")
        d.renkli_yaz("Kirmizi yazi", renk="kirmizi")
        d.renkli_yaz("Sari yazi", renk="sari")
        assert True

    def test_renkli_yaz_gecersiz_renk(self):
        """Gecersiz renk ile cagri."""
        d = Display()
        d.renkli_yaz("Test", renk="bilinmeyen")
        assert True

    def test_tablo(self):
        """Tablo formatlama."""
        d = Display()
        basliklar = ["Ad", "Yas", "Sehir"]
        satirlar = [["Ali", "30", "Istanbul"], ["Ayse", "25", "Ankara"]]
        d.tablo(basliklar, satirlar)
        assert True

    def test_tablo_bos(self):
        """Bos tablo formatlama."""
        d = Display()
        d.tablo(["Kol1", "Kol2"], [])
        assert True

    def test_progress_bar(self):
        """Progress bar gosterme."""
        d = Display()
        d.progress_bar(5, 10, baslik="Test")
        assert True

    def test_progress_bar_tamam(self):
        """Progress bar tamamlandi."""
        d = Display()
        d.progress_bar(10, 10, baslik="Bitti")
        assert True

    def test_progress_bar_sifir(self):
        """Progress bar sifir."""
        d = Display()
        d.progress_bar(0, 10)
        assert True

    def test_renkler_sabiti(self):
        """RENKLER sabiti."""
        assert "kirmizi" in Display.RENKLER
        assert "yesil" in Display.RENKLER
        assert "mavi" in Display.RENKLER


class TestHumanInterface:
    def test_human_interface_olusturma(self):
        """HumanInterface baslatma."""
        ui = HumanInterface()
        assert ui is not None
        assert ui._genislik == 50

    def test_progress_bar(self):
        """Progress bar gosterme."""
        ui = HumanInterface()
        ui.progress_bar(mevcut=5, toplam=10, baslik="Isleniyor")
        assert True

    def test_progress_bar_bitti(self):
        """Progress bar bitis."""
        ui = HumanInterface()
        ui.progress_bar(mevcut=10, toplam=10)
        assert True

    def test_onay_fonksiyonu(self):
        """onay() metodu varligi."""
        ui = HumanInterface()
        assert hasattr(ui, "onay") or hasattr(ui, "onayla") or hasattr(ui, "confirm")


class TestOnboarding:
    def test_onboarding_olusturma(self):
        """OnboardingWizard baslatma."""
        ow = OnboardingWizard()
        assert ow is not None

    def test_baslat_method(self):
        """baslat() metodu varligi."""
        ow = OnboardingWizard()
        assert hasattr(ow, "baslat") or hasattr(ow, "start")

    def test_config_kontrol(self):
        """config_kontrol() metodu varligi."""
        ow = OnboardingWizard()
        assert hasattr(ow, "config_kontrol") or hasattr(ow, "config_kontrol_et")
