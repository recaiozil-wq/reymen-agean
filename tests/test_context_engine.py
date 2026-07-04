# -*- coding: utf-8 -*-
"""
test_context_engine.py — context_engine.py testleri (~30 test)
"""

import pytest
import sys
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Import helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def engine():
    """Varsayılan ContextEngine örneği."""
    from context_engine import ContextEngine

    return ContextEngine(max_token=8000)


@pytest.fixture
def engine_small():
    """Küçük token limitli ContextEngine."""
    from context_engine import ContextEngine

    return ContextEngine(max_token=50)


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------


class TestInit:
    def test_default_max_token(self):
        from context_engine import ContextEngine

        ce = ContextEngine()
        assert ce.max_token == 8000

    def test_custom_max_token(self):
        from context_engine import ContextEngine

        ce = ContextEngine(max_token=4096)
        assert ce.max_token == 4096

    def test_zero_max_token(self):
        from context_engine import ContextEngine

        ce = ContextEngine(max_token=0)
        assert ce.max_token == 0

    def test_negative_max_token(self):
        from context_engine import ContextEngine

        ce = ContextEngine(max_token=-100)
        assert ce.max_token == -100


# ---------------------------------------------------------------------------
# _token_hesapla
# ---------------------------------------------------------------------------


class TestTokenHesapla:
    def test_bos_gecmis(self, engine):
        assert engine._token_hesapla([]) == 0

    def test_tek_mesaj(self, engine):
        gecmis = [{"icerik": "merhaba dunya"}]
        # 13 chars / 4 = 3
        assert engine._token_hesapla(gecmis) == 3

    def test_coklu_mesaj(self, engine):
        gecmis = [
            {"icerik": "birinci mesaj"},
            {"icerik": "ikinci mesaj"},
        ]
        # 26 chars / 4 = 6
        assert engine._token_hesapla(gecmis) == 6

    def test_content_fallback(self, engine):
        gecmis = [{"content": "content alani"}]
        # 13 chars / 4 = 3
        assert engine._token_hesapla(gecmis) == 3

    def test_icerik_oncelikli(self, engine):
        gecmis = [{"icerik": "birincil", "content": "ikincil"}]
        assert engine._token_hesapla(gecmis) == 2  # "birincil" = 8 chars

    def test_ek_metin_eklenir(self, engine):
        gecmis = [{"icerik": "abc"}]
        assert engine._token_hesapla(gecmis, "ekst") == 1  # (3 + 4) / 4 = 1

    def test_hem_icerik_hem_content_bos(self, engine):
        gecmis = [{"icerik": ""}]
        assert engine._token_hesapla(gecmis) == 0

    def test_karisik_anahtarlar(self, engine):
        gecmis = [
            {"icerik": "onemli not"},
            {"content": "digeri"},
        ]
        # "onemli not" (10 chars) + "digeri" (6 chars) = 16 / 4 = 4
        assert engine._token_hesapla(gecmis) == 4


# ---------------------------------------------------------------------------
# _ozetle
# ---------------------------------------------------------------------------


class TestOzetle:
    def test_bos_gecmis_icin_bos_ozet(self, engine):
        assert engine._ozetle([]) == ""

    def test_4_mesaj_icin_bos_ozet(self, engine):
        gecmis = [
            {"icerik": "a" * 10},
            {"icerik": "b" * 10},
            {"icerik": "c" * 10},
            {"icerik": "d" * 10},
        ]
        assert engine._ozetle(gecmis) == ""

    def test_5_mesaj_icin_ozet_var(self, engine):
        gecmis = [
            {"icerik": "a" * 10},
            {"icerik": "b" * 10},
            {"icerik": "c" * 10},
            {"icerik": "d" * 10},
            {"icerik": "e" * 10},
        ]
        ozet = engine._ozetle(gecmis)
        assert ozet != ""

    def test_ozet_son_3_mesaji_icerir(self, engine):
        """Son 3 mesaj ozet disi kalir."""
        gecmis = [
            {"icerik": "ilk"},
            {"icerik": "orta"},
            {"icerik": "son"},
            {"icerik": "atlanan1"},
            {"icerik": "atlanan2"},
            {"icerik": "atlanan3"},
        ]
        ozet = engine._ozetle(gecmis)
        assert "ilk" in ozet
        assert "orta" in ozet
        assert "son" in ozet
        assert "atlanan1" not in ozet
        assert "atlanan2" not in ozet
        assert "atlanan3" not in ozet

    def test_ozet_80_karakterle_sinirli(self, engine):
        gecmis = []
        for i in range(8):
            gecmis.append({"icerik": "x" * 100})
        ozet = engine._ozetle(gecmis)
        # Her bir parcada en fazla 80 karakter
        for parca in ozet.split(" | "):
            assert len(parca) <= 80

    def test_content_fallback_ozet(self, engine):
        gecmis = [
            {"content": "ilk mesaj"},
            {"content": "orta mesaj"},
            {"content": "son mesaj"},
            {"content": "devam"},
            {"content": "bitti"},
        ]
        ozet = engine._ozetle(gecmis)
        assert "ilk mesaj" in ozet
        assert "orta mesaj" in ozet

    def test_icerik_oncelikli_ozet(self, engine):
        gecmis = [
            {"icerik": "birincil", "content": "ikincil"},
            {"content": "sadece content"},
            {"content": "uc"},
            {"content": "dort"},
            {"content": "bes"},
        ]
        ozet = engine._ozetle(gecmis)
        assert "birincil" in ozet


# ---------------------------------------------------------------------------
# _onemli_bilgileri_ayikla
# ---------------------------------------------------------------------------


class TestOnemliBilgileriAyikla:
    def test_bos_gecmis_icin_bos(self, engine):
        assert engine._onemli_bilgileri_ayikla([]) == ""

    def test_anahtar_kelime_bulur(self, engine):
        gecmis = [{"icerik": "hedef projeyi tamamlamak"}]
        sonuc = engine._onemli_bilgileri_ayikla(gecmis)
        assert "hedef" in sonuc

    def test_anahtar_bulunamazsa_bos(self, engine):
        gecmis = [{"icerik": "bugun hava guzel"}]
        assert engine._onemli_bilgileri_ayikla(gecmis) == ""

    def test_coklu_anahtar_kelime(self, engine):
        gecmis = [
            {"icerik": "hedefimiz API gelistirmek"},
            {"icerik": "dosya yolu /tmp/test"},
        ]
        sonuc = engine._onemli_bilgileri_ayikla(gecmis)
        assert "hedefimiz api" in sonuc
        assert "dosya yolu" in sonuc

    def test_content_fallback_onemli(self, engine):
        gecmis = [{"content": "proje teslim tarihi"}]
        sonuc = engine._onemli_bilgileri_ayikla(gecmis)
        assert "proje" in sonuc

    def test_anahtar_kelime_listesi_kapsamli(self, engine):
        """Tum onemli anahtar kelimeler test edilir."""
        from context_engine import _ONEMLI_ANAHTAR

        assert "hedef" in _ONEMLI_ANAHTAR
        assert "hata" in _ONEMLI_ANAHTAR
        assert "api" in _ONEMLI_ANAHTAR
        assert "dosya" in _ONEMLI_ANAHTAR
        assert "proje" in _ONEMLI_ANAHTAR
        assert "görev" in _ONEMLI_ANAHTAR
        assert "key" in _ONEMLI_ANAHTAR

    def test_turkce_karakter_duyarliligi(self, engine):
        """şifre, görev gibi Turkce karakterler aranir."""
        gecmis = [{"icerik": "şifre: 12345"}]
        sonuc = engine._onemli_bilgileri_ayikla(gecmis)
        assert "şifre" in sonuc

    def test_100_karakter_siniri(self, engine):
        gecmis = [{"icerik": "hedef " + "x" * 200}]
        sonuc = engine._onemli_bilgileri_ayikla(gecmis)
        assert len(sonuc) <= 105  # lowercased + max 100 chars

    def test_tekrarlanan_anahtar_kelime(self, engine):
        gecmis = [
            {"icerik": "hedef bir"},
            {"icerik": "hedef iki"},
        ]
        sonuc = engine._onemli_bilgileri_ayikla(gecmis)
        parcalar = sonuc.split(" | ")
        assert len(parcalar) == 2


# ---------------------------------------------------------------------------
# baglam_hazirla
# ---------------------------------------------------------------------------


class TestBaglamHazirla:
    def test_return_type(self, engine):
        gecmis = [{"icerik": "hedef belirle"}]
        sonuc = engine.baglam_hazirla(gecmis, "devam")
        assert isinstance(sonuc, dict)
        assert "ozet" in sonuc
        assert "onemli" in sonuc
        assert "yeni_mesaj" in sonuc
        assert "token_tahmini" in sonuc

    def test_yeni_mesaj_korunur(self, engine):
        gecmis = []
        sonuc = engine.baglam_hazirla(gecmis, "test mesaji")
        assert sonuc["yeni_mesaj"] == "test mesaji"

    def test_token_tahmini_dogru(self, engine):
        gecmis = [{"icerik": "abc"}]
        sonuc = engine.baglam_hazirla(gecmis, "xy")
        # (3 + 2) / 4 = 1
        assert sonuc["token_tahmini"] == 1

    def test_bos_gecmis(self, engine):
        sonuc = engine.baglam_hazirla([], "merhaba")
        assert sonuc["ozet"] == ""
        assert sonuc["onemli"] == ""
        assert sonuc["token_tahmini"] == 1  # "merhaba" = 7 chars / 4 = 1

    def test_anahtar_kelime_gecmiste(self, engine):
        gecmis = [{"icerik": "API anahtari kayboldu"}]
        sonuc = engine.baglam_hazirla(gecmis, "devam")
        assert "api" in sonuc["onemli"]


# ---------------------------------------------------------------------------
# token_limit_asti_mi
# ---------------------------------------------------------------------------


class TestTokenLimitAstiMi:
    def test_limit_alti(self, engine):
        gecmis = [{"icerik": "kisa"}]
        assert engine.token_limit_asti_mi(gecmis) is False

    def test_limit_ustu(self, engine_small):
        gecmis = [{"icerik": "x" * 300}]
        assert engine_small.token_limit_asti_mi(gecmis) is True

    def test_tam_limitte(self, engine):
        gecmis = [{"icerik": "x" * 32000}]
        # 32000 / 4 = 8000 = max_token
        assert engine.token_limit_asti_mi(gecmis) is False

    def test_ek_metinle_asim(self, engine_small):
        gecmis = [{"icerik": "x" * 120}]
        assert engine_small.token_limit_asti_mi(gecmis, "y" * 120) is True

    def test_bos_gecmis_asimaz(self, engine_small):
        assert engine_small.token_limit_asti_mi([]) is False


# ---------------------------------------------------------------------------
# modul sabitleri
# ---------------------------------------------------------------------------


class TestModulSabitleri:
    def test_onemli_anahtar_listesi(self):
        from context_engine import _ONEMLI_ANAHTAR

        assert isinstance(_ONEMLI_ANAHTAR, list)
        assert len(_ONEMLI_ANAHTAR) >= 15

    def test_anahtar_kelimeler_unique(self):
        from context_engine import _ONEMLI_ANAHTAR

        assert len(_ONEMLI_ANAHTAR) == len(set(_ONEMLI_ANAHTAR))

    def test_import_hatasiz(self):
        """context_engine.py import edilirken hata firlatmamali."""
        try:
            import context_engine

            assert hasattr(context_engine, "ContextEngine")
        except Exception as e:
            pytest.fail(f"Import hatasi: {e}")


# ---------------------------------------------------------------------------
# __main__ test
# ---------------------------------------------------------------------------


class TestMainOrnek:
    def test_main_ornek_calisir(self):
        """__main__ blogundaki ornek calismali."""
        from context_engine import ContextEngine

        ce = ContextEngine(max_token=8000)
        gecmis = [{"icerik": "Hedefimiz Python yazilimi gelistirmek"}]
        sonuc = ce.baglam_hazirla(gecmis, "devam edelim")
        assert sonuc["ozet"] == ""
        assert "hedefimiz" in sonuc["onemli"]
        assert sonuc["yeni_mesaj"] == "devam edelim"
