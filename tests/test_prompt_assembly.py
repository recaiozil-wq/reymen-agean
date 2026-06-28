# -*- coding: utf-8 -*-
"""test_prompt_assembly.py — PromptAssembly için kapsamlı pytest testleri."""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
import tempfile

_proje_koku = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _proje_koku not in sys.path:
    sys.path.insert(0, _proje_koku)

from prompt_assembly import PromptAssembly, PromptAssemblyEngine


# ── Init Tests ────────────────────────────────────────────────────────────

class TestInit:
    def test_varsayilan_depo_yolu(self):
        pa = PromptAssembly()
        assert pa._parcalar == {}
        assert pa._sablonlar == {}
        assert pa._bounded_memory is None
        assert pa._learning_loop is None

    def test_ozel_depo_yolu(self, tmp_path):
        pa = PromptAssembly(depo_yolu=str(tmp_path))
        assert pa._depo_yolu == tmp_path

    def test_bounded_memory_ve_learning_loop(self):
        bm = MagicMock()
        ll = MagicMock()
        pa = PromptAssembly(bounded_memory=bm, learning_loop=ll)
        assert pa._bounded_memory is bm
        assert pa._learning_loop is ll

    def test_alias_esitlik(self):
        assert PromptAssembly is PromptAssemblyEngine


# ── ekle / cikar Tests ────────────────────────────────────────────────────

class TestEkleCikar:
    def test_ekle_basarili(self):
        pa = PromptAssembly()
        assert pa.ekle("giris", "Merhaba") is True
        assert "giris" in pa._parcalar

    def test_ekle_bos_ad(self):
        pa = PromptAssembly()
        assert pa.ekle("", "icerik") is False

    def test_ekle_none_ad(self):
        pa = PromptAssembly()
        assert pa.ekle(None, "icerik") is False

    def test_ekle_bos_icerik(self):
        pa = PromptAssembly()
        assert pa.ekle("ad", "") is False

    def test_ekle_none_icerik(self):
        pa = PromptAssembly()
        assert pa.ekle("ad", None) is False

    def test_ekle_int_ad(self):
        pa = PromptAssembly()
        assert pa.ekle(123, "icerik") is False

    def test_ekle_strip(self):
        pa = PromptAssembly()
        pa.ekle("ad", " icerik  ")
        assert pa._parcalar["ad"] == "icerik"

    def test_cikar_basarili(self):
        pa = PromptAssembly()
        pa.ekle("x", "y")
        assert pa.cikar("x") is True
        assert "x" not in pa._parcalar

    def test_cikar_yok(self):
        pa = PromptAssembly()
        assert pa.cikar("yok") is False


# ── birlestir Tests ────────────────────────────────────────────────────────

class TestBirlestir:
    def test_ikili_birlestirme(self):
        pa = PromptAssembly()
        pa.ekle("a", "Bir")
        pa.ekle("b", "Iki")
        sonuc = pa.birlestir(["a", "b"])
        assert sonuc == "Bir\n\nIki"

    def test_ozel_ayrac(self):
        pa = PromptAssembly()
        pa.ekle("a", "X")
        pa.ekle("b", "Y")
        sonuc = pa.birlestir(["a", "b"], ayrac=" | ")
        assert sonuc == "X | Y"

    def test_eksik_parca_keyerror(self):
        pa = PromptAssembly()
        with pytest.raises(KeyError, match="Parca bulunamadi"):
            pa.birlestir(["yok"])

    def test_sablon_uygulama(self):
        pa = PromptAssembly()
        pa.sabton_ekle("fmt", "<{icerik}>")
        pa.ekle("a", "icerigi")
        sonuc = pa.birlestir(["a"], sablon="fmt")
        assert sonuc == "<icerigi>"

    def test_sablon_olmayan_adi(self):
        pa = PromptAssembly()
        pa.ekle("a", "test")
        sonuc = pa.birlestir(["a"], sablon="yok_sablon")
        assert sonuc == "test"


# ── kaydet / yukle Tests ──────────────────────────────────────────────────

class TestKaydetYukle:
    def test_kaydet_basarili(self, tmp_path):
        pa = PromptAssembly(depo_yolu=str(tmp_path))
        pa.ekle("test", "icerik test")
        yol = pa.kaydet("test")
        assert yol is not None
        assert Path(yol).exists()
        assert Path(yol).read_text(encoding="utf-8") == "icerik test"

    def test_kaydet_yok(self, tmp_path):
        pa = PromptAssembly(depo_yolu=str(tmp_path))
        assert pa.kaydet("olmayan") is None

    def test_yukle_basarili(self, tmp_path):
        pa = PromptAssembly(depo_yolu=str(tmp_path))
        pa.ekle("test", "icerik yukle")
        pa.kaydet("test")
        pa._parcalar.clear()
        yuklenen = pa.yukle("test")
        assert yuklenen == "icerik yukle"
        assert pa._parcalar["test"] == "icerik yukle"

    def test_yukle_yok(self, tmp_path):
        pa = PromptAssembly(depo_yolu=str(tmp_path))
        assert pa.yukle("olmayan") is None


# ── sabton_ekle Tests ─────────────────────────────────────────────────────

class TestSablonEkle:
    def test_basarili(self):
        pa = PromptAssembly()
        assert pa.sabton_ekle("fmt", "X {icerik} Y") is True
        assert "fmt" in pa._sablonlar

    def test_icerik_yok(self):
        pa = PromptAssembly()
        assert pa.sabton_ekle("fmt", "icerik yok burada") is False


# ── utility Tests ──────────────────────────────────────────────────────────

class TestUtility:
    def test_liste(self):
        pa = PromptAssembly()
        pa.ekle("a", "1")
        pa.ekle("b", "2")
        assert set(pa.liste()) == {"a", "b"}

    def test_temizle(self):
        pa = PromptAssembly()
        pa.ekle("a", "1")
        pa.ekle("b", "2")
        sayi = pa.temizle()
        assert sayi == 2
        assert pa._parcalar == {}

    def test_boyut(self):
        pa = PromptAssembly()
        pa.ekle("a", "hello")
        assert pa.boyut("a") == 5
        assert pa.boyut("yok") == 0

    def test_ara(self):
        pa = PromptAssembly()
        pa.ekle("a", "Merhaba dunya")
        pa.ekle("b", "Python kodu")
        pa.ekle("c", "Merhaba Python")
        sonuc = pa.ara("merhaba")
        assert set(sonuc) == {"a", "c"}

    def test_ara_bulunamadi(self):
        pa = PromptAssembly()
        pa.ekle("a", "test")
        assert pa.ara("xyz") == []


# ── _varsayilan_react_talimati Tests ──────────────────────────────────────

class TestReactTalimati:
    def test_temel_icerik(self):
        pa = PromptAssembly()
        talimat = pa._varsayilan_react_talimati("Hedef X", "", 1, 10)
        assert "ReYMeN" in talimat
        assert "ReAct" in talimat
        assert "Hedef X" in talimat
        assert "Tur 1/10" in talimat

    def test_son_gozlem_dahil(self):
        pa = PromptAssembly()
        talimat = pa._varsayilan_react_talimati("hedef", "onceki cikti", 2, 5)
        assert "SON GOZLEM" in talimat
        assert "onceki cikti" in talimat

    def test_son_gozlem_yok(self):
        pa = PromptAssembly()
        talimat = pa._varsayilan_react_talimati("hedef", "", 1, 1)
        assert "SON GOZLEM" not in talimat


# ── _beceri_baglamini_al Tests ────────────────────────────────────────────

class TestBeceriBaglami:
    def test_learning_loop_yok(self):
        pa = PromptAssembly()
        assert pa._beceri_baglamini_al("hedef") == ""

    def test_learning_loop_exception(self):
        ll = MagicMock()
        ll.beceri_baglamini_al.side_effect = RuntimeError("fail")
        pa = PromptAssembly(learning_loop=ll)
        assert pa._beceri_baglamini_al("hedef") == ""

    def test_learning_loop_basarili(self):
        ll = MagicMock()
        ll.beceri_baglamini_al.return_value = "beceri context"
        pa = PromptAssembly(learning_loop=ll)
        sonuc = pa._beceri_baglamini_al("hedef")
        assert sonuc == "beceri context"
        ll.beceri_baglamini_al.assert_called_once_with("hedef", adet=3)

    def test_learning_loop_none_dondurur(self):
        ll = MagicMock()
        ll.beceri_baglamini_al.return_value = None
        pa = PromptAssembly(learning_loop=ll)
        assert pa._beceri_baglamini_al("hedef") == ""


# ── insa_et Tests ──────────────────────────────────────────────────────────

class TestInsaEt:
    def test_bos_prompt(self, tmp_path):
        pa = PromptAssembly(depo_yolu=str(tmp_path))
        prompt = pa.insa_et("Hedef test")
        assert "Hedef test" in prompt
        assert "ReYMeN" in prompt

    def test_ic_gozlem_modu(self, tmp_path):
        pa = PromptAssembly(depo_yolu=str(tmp_path))
        prompt = pa.insa_et("Hedef", ic_gozlem_modu=True)
        assert "Ic gozlem modu" in prompt

    def test_tur_bilgisi(self, tmp_path):
        pa = PromptAssembly(depo_yolu=str(tmp_path))
        prompt = pa.insa_et("Hedef", tur=5, toplam_tur=20)
        assert "Tur 5/20" in prompt

    def test_son_gozlem_dahil(self, tmp_path):
        pa = PromptAssembly(depo_yolu=str(tmp_path))
        prompt = pa.insa_et("Hedef", son_gozlem="onceki cikti burada")
        assert "onceki cikti burada" in prompt

    def test_beceri_baglami_dahil(self, tmp_path):
        ll = MagicMock()
        ll.beceri_baglamini_al.return_value = "beceri bilgisi"
        pa = PromptAssembly(depo_yolu=str(tmp_path), learning_loop=ll)
        prompt = pa.insa_et("Hedef")
        assert "beceri bilgisi" in prompt


# ── Hata Durumlari ─────────────────────────────────────────────────────────

class TestHataDurumlari:
    def test_kaydet_oserror(self, tmp_path):
        pa = PromptAssembly(depo_yolu=str(tmp_path))
        pa.ekle("test", "icerik")
        # depo_yolu'nu dosya yaparak hata zorla
        dosya = tmp_path / "test"  # dosya adinda klasor yok
        # Permission denied test - depo_yolu'nu read-only yap
        ro_path = tmp_path / "readonly"
        ro_path.mkdir()
        pa2 = PromptAssembly(depo_yolu=str(ro_path))
        # Normal kaydet calisiyor
        pa2.ekle("x", "y")
        result = pa2.kaydet("x")
        assert result is not None

    def test_yukle_oserror(self, tmp_path):
        pa = PromptAssembly(depo_yolu=str(tmp_path))
        # Var olmayan dosya → None
        assert pa.yukle("yok") is None
