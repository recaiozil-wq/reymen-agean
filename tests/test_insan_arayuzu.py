# -*- coding: utf-8 -*-
"""
test_insan_arayuzu.py — HumanInterface kapsamli testleri.

29 spesifik test + ek kosullar.
input/onay/onay_iste icin monkeypatch ile simulate.
"""

import sys
from pathlib import Path

PROJ_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJ_ROOT))

import pytest
from insan_arayuzu import HumanInterface, InsanArayuzu


# ── Fikstür ─────────────────────────────────────────────────────────


@pytest.fixture
def ui():
    return HumanInterface(genislik=20, sembol="=", bos_sembol=".")


# ── 1. __init__ Testleri ──────────────────────────────────────────


class TestInit:
    """1. __init__ — genislik dogru set, _genislik alias var."""

    def test_varsayilan_genislik(self):
        ui = HumanInterface()
        assert ui.genislik == 50
        assert ui._genislik == 50

    def test_ozel_genislik(self):
        ui = HumanInterface(genislik=30)
        assert ui.genislik == 30
        assert ui._genislik == 30

    def test_ozel_sembol_bos_sembol(self):
        ui = HumanInterface(sembol="#", bos_sembol="-")
        assert ui.sembol == "#"
        assert ui.bos_sembol == "-"

    def test_genislik_alias(self):
        """_genislik alias 'i genislik ile ayni degeri doner."""
        ui = HumanInterface(genislik=42)
        assert ui._genislik == ui.genislik == 42


# ── 2-11. progress_bar() Testleri ──────────────────────────────────


class TestProgressBar:
    """2-11: progress_bar testleri."""

    # 2: 0/10 -> "[....................]"  (20*".")
    def test_0_10_bos_bar(self, ui):
        sonuc = ui.progress_bar(0, 10, goster_yuzde=False, goster_sayi=False)
        beklenen_bar = "[" + "." * 20 + "]"
        assert beklenen_bar in sonuc, f"Beklenen: {beklenen_bar}, alinan: {sonuc}"

    # 3: 10/10 -> "[====================]"  (20*"=")
    def test_10_10_dolu_bar(self, ui):
        sonuc = ui.progress_bar(10, 10, goster_yuzde=False, goster_sayi=False)
        beklenen_bar = "[" + "=" * 20 + "]"
        assert beklenen_bar in sonuc, f"Beklenen: {beklenen_bar}, alinan: {sonuc}"

    # 4: 5/10, goster_yuzde=True -> "%50" iceriyor
    def test_5_10_yuzde_goster(self, ui):
        sonuc = ui.progress_bar(5, 10, goster_yuzde=True, goster_sayi=False)
        assert "%50.0" in sonuc

    # 5: 5/10, goster_sayi=True -> "5/10" iceriyor
    def test_5_10_sayi_goster(self, ui):
        sonuc = ui.progress_bar(5, 10, goster_yuzde=False, goster_sayi=True)
        assert "5/10" in sonuc

    # 6: toplam=0 -> "[Progress: gecersiz deger]"
    def test_toplam_sifir(self, ui):
        sonuc = ui.progress_bar(0, 0)
        assert sonuc == "[Progress: gecersiz deger]"

    # 7: toplam=-5 -> "[Progress: gecersiz deger]"
    def test_toplam_negatif(self, ui):
        sonuc = ui.progress_bar(5, -5)
        assert sonuc == "[Progress: gecersiz deger]"

    # 8: mevcut > toplam -> min(100, ...) ile sinirli
    def test_mevcut_asim(self, ui):
        sonuc = ui.progress_bar(20, 10, goster_yuzde=True, goster_sayi=False)
        assert "%100.0" in sonuc

    # 9: mevcut < 0 -> max(0, ...) ile sinirli
    def test_mevcut_negatif(self, ui):
        sonuc = ui.progress_bar(-5, 10, goster_yuzde=True, goster_sayi=False)
        assert "%0.0" in sonuc

    # 10: baslik eklenince string'de baslik gorunuyor
    def test_baslik_goster(self, ui):
        sonuc = ui.progress_bar(5, 10, baslik="Isleniyor")
        assert "Isleniyor" in sonuc

    # 11: farkli sembol ve bos_sembol ile (ornek "#" ve "-")
    def test_farkli_sembol(self):
        ui = HumanInterface(genislik=10, sembol="#", bos_sembol="-")
        sonuc = ui.progress_bar(5, 10, goster_yuzde=False, goster_sayi=False)
        assert "[#####-----]" in sonuc, f"Beklenen '[#####-----]', alinan: {sonuc}"

    # Ek: goster_yuzde=False, goster_sayi=False -> sadece bar
    def test_sadece_bar(self, ui):
        sonuc = ui.progress_bar(5, 10, goster_yuzde=False, goster_sayi=False)
        assert "%" not in sonuc
        assert "/" not in sonuc


# ── 12-16. tablo() Testleri ────────────────────────────────────────


class TestTablo:
    """12-16: tablo testleri."""

    # 12: 3 satir 2 sutun -> dogru format
    def test_3_satir_2_sutun(self, ui):
        veri = [
            {"ad": "Ali", "yas": "20"},
            {"ad": "Veli", "yas": "30"},
            {"ad": "Ayse", "yas": "25"},
        ]
        sonuc = ui.tablo(veri)
        assert "Ali" in sonuc
        assert "Veli" in sonuc
        assert "Ayse" in sonuc
        assert "ad" in sonuc
        assert "yas" in sonuc
        assert sonuc.count("\n") >= 5  # ayrac + baslik + ayrac + 3 satir + ayrac

    # 13: bos liste -> "[Tablo: veri yok]"
    def test_bos_veri(self, ui):
        sonuc = ui.tablo([])
        assert sonuc == "[Tablo: veri yok]"

    # 14: basliklar parametresi ile -> baslik satiri var
    def test_basliklar_ozel(self, ui):
        veri = [{"x": "1", "y": "2"}]
        sonuc = ui.tablo(veri, basliklar=["X", "Y"])
        assert "X" in sonuc
        assert "Y" in sonuc
        assert "x" not in sonuc  # sadece belirtilen baslik

    # 15: max_genislik ile -> satirlar kisaltiliyor
    def test_max_genislik_kesme(self, ui):
        veri = [{"metin": "a" * 100}]
        sonuc = ui.tablo(veri, basliklar=["metin"], max_sutun=10)
        assert "..." in sonuc

    # 16: tek satir -> dogru
    def test_tek_satir(self, ui):
        veri = [{"isim": "Tek"}]
        sonuc = ui.tablo(veri)
        assert "Tek" in sonuc
        assert "isim" in sonuc


# ── 17-19. menu() Testleri ─────────────────────────────────────────


class TestMenu:
    """17-19: menu testleri."""

    # 17: monkeypatch ile "1" cevabi -> "secenek_1"
    def test_secim_1(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "1")
        ui = HumanInterface()
        sonuc = ui.menu(
            "Ana Menu", [("secenek_1", "Ilk Secim"), ("secenek_2", "Ikinci Secim")]
        )
        assert sonuc == "secenek_1"

    # 18: gecersiz secim (monkeypatch "abc") -> tekrar sor
    def test_gecersiz_secim_abc(self, monkeypatch):
        inputs = iter(["abc", "2"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        ui = HumanInterface()
        sonuc = ui.menu("Menu", [("x", "X"), ("y", "Y")])
        assert sonuc == "y"

    # 19: secenek listesi bos -> ""
    def test_bos_secenek(self, ui, monkeypatch):
        sonuc = ui.menu("Baslik", [])
        assert sonuc == ""

    # Ek: anahtar ile secim
    def test_anahtar_ile_secim(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "b")
        ui = HumanInterface()
        sonuc = ui.menu("Test", [("a", "A Secenegi"), ("b", "B Secenegi")])
        assert sonuc == "b"

    # Ek: EOFError -> ilk secenek
    def test_eof_first(self, monkeypatch):
        monkeypatch.setattr(
            "builtins.input", lambda _: (_ for _ in ()).throw(EOFError())
        )
        ui = HumanInterface()
        sonuc = ui.menu("Test", [("ilk", "Ilk Secim")])
        assert sonuc == "ilk"


# ── 20. run() Testleri ─────────────────────────────────────────────


class TestRun:
    """20: run — str donuyor mu (hata yok)."""

    def test_run_str_donuyor(self):
        ui = HumanInterface()
        sonuc = ui.run()
        assert isinstance(sonuc, str)

    def test_run_progress_bar_action(self, ui):
        sonuc = ui.run(action="progress_bar", mevcut=5, toplam=10)
        assert "%50.0" in sonuc

    def test_run_input_action(self, ui, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "girdi")
        sonuc = ui.run(action="input", prompt="Ad?")
        assert sonuc == "girdi"

    def test_run_onay_action(self, ui, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "e")
        sonuc = ui.run(action="onay", mesaj="Onay?")
        assert sonuc == "True"

    def test_run_tablo_action(self, ui):
        sonuc = ui.run(action="tablo", veri=[{"a": 1}])
        assert "1" in sonuc

    def test_run_menu_action(self, ui, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "1")
        sonuc = ui.run(action="menu", baslik="M", secenekler=[("a", "A")])
        assert sonuc == "a"

    def test_run_bilinmeyen_action(self, ui):
        sonuc = ui.run(action="yok")
        assert "Bilinmeyen" in sonuc

    def test_run_varsayilan_action(self, ui):
        sonuc = ui.run(mevcut=5, toplam=10)
        assert "%50.0" in sonuc

    def test_run_hata_yakalama(self, ui):
        """progress_bar hata firlatirsa run yakalar."""
        sonuc = ui.run(action="progress_bar", mevcut=5, toplam=10)
        assert isinstance(sonuc, str)


# ── 21-23. onay() Testleri ─────────────────────────────────────────


class TestOnay:
    """21-23: onay testleri."""

    # 21: monkeypatch "e" -> True
    def test_onay_evet(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "e")
        ui = HumanInterface()
        assert ui.onay("Devam?") is True

    # 22: monkeypatch "h" -> False
    def test_onay_hayir(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "h")
        ui = HumanInterface()
        assert ui.onay("Devam?") is False

    # 23: monkeypatch "enter" (bos) -> varsayilan=True ile True
    def test_onay_bos_varsayilan_true(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "")
        ui = HumanInterface()
        assert ui.onay("Devam?", varsayilan=True) is True

    # Ek: bos, varsayilan=False -> False
    def test_onay_bos_varsayilan_false(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "")
        ui = HumanInterface()
        assert ui.onay("Devam?", varsayilan=False) is False

    # Ek: "y" -> True
    def test_onay_y_kisa(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "y")
        ui = HumanInterface()
        assert ui.onay("Devam?") is True

    # Ek: "n" -> False
    def test_onay_n_kisa(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "n")
        ui = HumanInterface()
        assert ui.onay("Devam?") is False

    # Ek: "yes" -> True
    def test_onay_yes(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "yes")
        ui = HumanInterface()
        assert ui.onay("Devam?") is True

    # Ek: "no" -> False
    def test_onay_no(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "no")
        ui = HumanInterface()
        assert ui.onay("Devam?") is False

    # Ek: EOFError -> varsayilan
    def test_onay_eof(self, monkeypatch):
        monkeypatch.setattr(
            "builtins.input", lambda _: (_ for _ in ()).throw(EOFError())
        )
        ui = HumanInterface()
        assert ui.onay("Devam?", varsayilan=False) is False

    # Ek: REYMEN_OTOMATIK_ONAY=true -> direkt True (conftest temizler, manuel set)
    def test_onay_otomatik_onay(self, monkeypatch):
        monkeypatch.setenv("REYMEN_OTOMATIK_ONAY", "true")
        ui = HumanInterface()
        # input hic cagrilmamali, direkt True doner
        assert ui.onay("Devam?") is True

    # Ek: REYMEN_OTOMATIK_ONAY=1 -> direkt True
    def test_onay_otomatik_onay_1(self, monkeypatch):
        monkeypatch.setenv("REYMEN_OTOMATIK_ONAY", "1")
        ui = HumanInterface()
        assert ui.onay("Devam?") is True


# ── 24. onay_iste() Testleri ───────────────────────────────────────


class TestOnayIste:
    """24: onay_iste testleri."""

    # 24: monkeypatch "e" -> True (ctypes fallback yolu)
    def test_onay_iste_evet_fallback(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "e")
        monkeypatch.setattr("ctypes.windll", None, raising=False)
        ui = HumanInterface()
        assert ui.onay_iste("Baslik", "Mesaj") is True

    # Ek: fallback red
    def test_onay_iste_hayir_fallback(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "h")
        monkeypatch.setattr("ctypes.windll", None, raising=False)
        ui = HumanInterface()
        assert ui.onay_iste("Baslik", "Mesaj") is False

    # Ek: ctypes MessageBoxW IDYES=6 -> True
    def test_onay_iste_ctypes_evet(self, monkeypatch):
        from unittest.mock import patch

        with patch("ctypes.windll.user32.MessageBoxW", return_value=6):
            ui = HumanInterface()
            assert ui.onay_iste("Test", "Onay?") is True

    # Ek: ctypes MessageBoxW IDYES!=6 -> False
    def test_onay_iste_ctypes_hayir(self, monkeypatch):
        from unittest.mock import patch

        with patch("ctypes.windll.user32.MessageBoxW", return_value=7):
            ui = HumanInterface()
            assert ui.onay_iste("Test", "Onay?") is False


# ── 25-28. input() Testleri ────────────────────────────────────────


class TestInput:
    """25-28: input testleri."""

    # 25: monkeypatch "selam" -> "selam"
    def test_basit_girdi(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "selam")
        ui = HumanInterface()
        assert ui.input("prompt") == "selam"

    # 26: secenekler=["a","b"] ile monkeypatch "a" -> "a"
    def test_secenek_gecerli(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "a")
        ui = HumanInterface()
        assert ui.input("sec", secenekler=["a", "b"]) == "a"

    # 27: secenekler=["a","b"] ile monkeypatch "c" -> tekrar sor
    def test_secenek_gecersiz(self, monkeypatch):
        inputs = iter(["c", "a"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        ui = HumanInterface()
        assert ui.input("sec", secenekler=["a", "b"]) == "a"

    # 28: varsayilan="x" ile monkeypatch "" -> "x"
    def test_varsayilan_bos(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "")
        ui = HumanInterface()
        assert ui.input("prompt", varsayilan="x") == "x"

    # Ek: varsayilan yok, bos -> ""
    def test_bos_varsayilan_yok(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "")
        ui = HumanInterface()
        assert ui.input("prompt") == ""

    # Ek: zorunlu=True, once bos sonra deger
    def test_zorunlu_once_bos(self, monkeypatch):
        inputs = iter(["", "deger"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        ui = HumanInterface()
        assert ui.input("Zorunlu:", zorunlu=True) == "deger"

    # Ek: EOFError -> varsayilan
    def test_eof_varsayilan(self, monkeypatch):
        monkeypatch.setattr(
            "builtins.input", lambda _: (_ for _ in ()).throw(EOFError())
        )
        ui = HumanInterface()
        assert ui.input("Test", varsayilan="varsay") == "varsay"

    # Ek: KeyboardInterrupt -> ""
    def test_keyboard_interrupt(self, monkeypatch):
        monkeypatch.setattr(
            "builtins.input", lambda _: (_ for _ in ()).throw(KeyboardInterrupt())
        )
        ui = HumanInterface()
        assert ui.input("Test") == ""


# ── 29. _konsol_boyut() Testleri ───────────────────────────────────


class TestKonsolBoyut:
    """29: _konsol_boyut — >= 20 donuyor."""

    def test_konsol_boyut_en_az_20(self):
        ui = HumanInterface()
        boyut = ui._konsol_boyut()
        assert boyut >= 20, f"_konsol_boyut={boyut}, beklenen >= 20"

    def test_konsol_boyut_tamsayi(self):
        ui = HumanInterface()
        boyut = ui._konsol_boyut()
        assert isinstance(boyut, int)


# ── Eski Ad Uyumlulugu ─────────────────────────────────────────────


class TestInsanArayuzuAlias:
    """InsanArayuzu eski ad uyumlulugu."""

    def test_insan_arayuzu_alias(self):
        ui = InsanArayuzu()
        assert isinstance(ui, HumanInterface)

    def test_insan_arayuzu_calisiyor(self):
        ui = InsanArayuzu(genislik=10)
        sonuc = ui.progress_bar(3, 10, baslik="Test")
        assert "Test" in sonuc


# ── Entegrasyon: Birden cok metod zinciri ──────────────────────────


class TestEntegrasyon:
    """Birden cok HumanInterface metodunun birlikte calismasi."""

    def test_progress_sonra_tablo(self):
        ui = HumanInterface(genislik=10)
        p = ui.progress_bar(5, 10, goster_sayi=False, goster_yuzde=False)
        t = ui.tablo([{"isim": "Test"}])
        assert isinstance(p, str)
        assert isinstance(t, str)
        assert "Test" in t

    def test_onay_sonra_input(self, monkeypatch):
        inputs = iter(["e", "merhaba"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        ui = HumanInterface()
        onay_sonuc = ui.onay("Devam?")
        girdi_sonuc = ui.input("Yaz:")
        assert onay_sonuc is True
        assert girdi_sonuc == "merhaba"
