# -*- coding: utf-8 -*-
"""test_anayasa_denetcisi.py — anayasa_denetcisi modülü için pytest testleri."""

import os
import sys
import re

import pytest

_proje_koku = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _proje_koku not in sys.path:
    sys.path.insert(0, _proje_koku)

from anayasa_denetcisi import (
    kural_varmi,
    mesaj_guvenli_mi,
    _KESIN_GEC,
    _ENGELLI_DESENLER,
    _KIBAR_IFADELER,
)


# ══════════════════════════════════════════════════════════════════════════
# kural_varmi testleri (1-15)
# ══════════════════════════════════════════════════════════════════════════


class TestKuralVarmi:
    # ── Boş/null girdi ────────────────────────────────────────────────────
    def test_bos_metin_gecer(self):
        """Boş metin güvenli kabul edilmeli."""
        engelli, gerekce = kural_varmi("")
        assert engelli is False
        assert gerekce == ""

    def test_none_metin_gecer(self):
        """None metin güvenli kabul edilmeli."""
        engelli, gerekce = kural_varmi(None)
        assert engelli is False
        assert gerekce == ""

    def test_bosluk_metin_gecer(self):
        """Sadece boşluk içeren metin güvenli kabul edilmeli."""
        engelli, gerekce = kural_varmi("   ")
        assert engelli is False

    # ── Kısa mesaj (≤5 kelime) otomatik geçer ────────────────────────────
    def test_kisa_mesaj_otomatik_gecer(self):
        """5 kelimeden kısa mesajlar otomatik geçmeli (engelli desen yoksa)."""
        engelli, gerekce = kural_varmi("Bugün hava çok güzel")
        assert engelli is False

    def test_tek_kelime_gecer(self):
        """Tek kelimelik mesaj geçmeli."""
        engelli, gerekce = kural_varmi("Merhaba")
        assert engelli is False

    def test_uc_url_kisa_mesaj_sayilmaz(self):
        """3+ URL (bitişik) varsa spam olarak yakalanmalı, kısa mesaj kuralından önce."""
        # Regex (https?://[^\s]+){3,} bitişik URL'leri eşleştirir (boşluksuz)
        engelli, gerekce = kural_varmi("http://x.comhttp://y.comhttp://z.com")
        assert engelli is True
        assert "Uygunsuz" in gerekce

    # ── Engelli desenler ─────────────────────────────────────────────────
    def test_sik_engellenir(self):
        """'sik' içeren saldırgan ifade engellenmeli."""
        engelli, gerekce = kural_varmi("siktir git")
        assert engelli is True
        assert "Uygunsuz" in gerekce

    def test_amk_engellenir(self):
        """'amk' içeren ifade engellenmeli."""
        engelli, gerekce = kural_varmi("amk seni")
        assert engelli is True

    def test_pic_engellenir(self):
        """'piç' içeren ifade engellenmeli."""
        engelli, gerekce = kural_varmi("piç herif")
        assert engelli is True

    def test_orospu_engellenir(self):
        """'orospu' içeren ifade engellenmeli."""
        engelli, gerekce = kural_varmi("orospu çocuğu")
        assert engelli is True

    def test_oroşpu_engellenir(self):
        """'oroşpu' (ş ile) içeren ifade engellenmeli."""
        engelli, gerekce = kural_varmi("oroşpu")
        assert engelli is True

    def test_bomba_yap_engellenir(self):
        """'bomba yap' ifadesi engellenmeli."""
        engelli, gerekce = kural_varmi("bomba yapmak istiyorum")
        assert engelli is True

    def test_nasil_oldur_engellenir(self):
        """'nasıl öldür' ifadesi engellenmeli."""
        engelli, gerekce = kural_varmi("nasıl öldürülür birini")
        assert engelli is True

    def test_zararli_yazilim_engellenir(self):
        """'zararlı yazılım' ifadesi engellenmeli."""
        engelli, gerekce = kural_varmi("zararlı yazılım nasıl yapılır")
        assert engelli is True

    def test_uc_url_spam_engellenir(self):
        """3+'den fazla URL (bitişik) spam olarak engellenmeli."""
        engelli, gerekce = kural_varmi(
            "http://example.comhttp://test.comhttp://demo.comhttp://more.com"
        )
        assert engelli is True

    # ── Güvenli mesajlar ─────────────────────────────────────────────────
    def test_normal_konusma_gecer(self):
        """Normal bir konuşma mesajı geçmeli."""
        engelli, gerekce = kural_varmi(
            "Proje dosyalarını nasıl düzenleyebilirim? Yardımcı olur musun?"
        )
        assert engelli is False

    def test_sadece_soru_gecer(self):
        """Basit bir soru geçmeli."""
        engelli, gerekce = kural_varmi("Bu projede hangi dosyalar var?")
        assert engelli is False

    def test_kesin_gec_listesi_calisir(self):
        """_KESIN_GEC listesindeki ifadeler geçmeli."""
        for ifade in ["merhaba", "selam", "teşekkür", "günaydın", "iyi geceler"]:
            engelli, gerekce = kural_varmi(ifade)
            assert engelli is False, f"{ifade!r} engellenmemeli"

    def test_kibar_ifade_iceriyorsa_gecer(self):
        """Kibar ifade (lütfen, rica, yardım) içeren mesaj geçmeli."""
        engelli, gerekce = kural_varmi(
            "Lütfen yardım eder misiniz? Çok teşekkür ederim."
        )
        assert engelli is False


# ══════════════════════════════════════════════════════════════════════════
# mesaj_guvenli_mi testleri (16-20)
# ══════════════════════════════════════════════════════════════════════════


class TestMesajGuvenliMi:
    def test_guvenli_mesaj_true(self):
        """Güvenli mesaj True dönmeli."""
        assert mesaj_guvenli_mi("Merhaba, nasılsın?") is True

    def test_tehlikeli_mesaj_false(self):
        """Tehlikeli mesaj False dönmeli."""
        assert mesaj_guvenli_mi("siktir git") is False

    def test_bos_mesaj_true(self):
        """Boş mesaj True dönmeli."""
        assert mesaj_guvenli_mi("") is True

    def test_spam_url_false(self):
        """Spam URL (bitişik 3+) içeren mesaj False dönmeli."""
        assert mesaj_guvenli_mi("http://a.comhttp://b.comhttp://c.com") is False

    def test_kesin_gec_true(self):
        """_KESIN_GEC'teki ifadeler True dönmeli."""
        assert mesaj_guvenli_mi("merhaba") is True


# ══════════════════════════════════════════════════════════════════════════
# Sabitler testleri (21-22)
# ══════════════════════════════════════════════════════════════════════════


class TestSabitler:
    def test_kesin_gec_frozenset(self):
        """_KESIN_GEC bir frozenset olmalı."""
        assert isinstance(_KESIN_GEC, frozenset)
        assert len(_KESIN_GEC) > 0

    def test_engelli_desenler_list(self):
        """_ENGELLI_DESENLER bir liste olmalı ve içinde regex'ler bulunmalı."""
        assert isinstance(_ENGELLI_DESENLER, list)
        assert len(_ENGELLI_DESENLER) > 0
        for desen in _ENGELLI_DESENLER:
            assert isinstance(desen, re.Pattern)

    def test_kibar_ifadeler_regex(self):
        """_KIBAR_IFADELER bir regex pattern olmalı."""
        assert isinstance(_KIBAR_IFADELER, re.Pattern)


# ══════════════════════════════════════════════════════════════════════════
# Karmaşık/köşe durum testleri (23-25)
# ══════════════════════════════════════════════════════════════════════════


class TestKoseDurumlari:
    def test_engelli_desen_kisa_mesajda_yakalanir(self):
        """Engelli desen kısa mesajda (>5 kelime olmasa bile) yakalanmalı."""
        engelli, gerekce = kural_varmi("siktir")
        assert engelli is True

    def test_cevresel_baglam_zararsiz(self):
        """Tehlikeli olmayan teknik bir terim yanlışlıkla engellenmemeli."""
        engelli, gerekce = kural_varmi(
            "Python'da os.path modülü ile dosya işlemleri yapıyorum."
        )
        assert engelli is False

    def test_karisik_durum_engelli_desen_ve_kibar_kelime(self):
        """Engelli desen varsa kibar kelime olsa bile engellemeli."""
        engelli, gerekce = kural_varmi("siktir git lütfen")
        assert engelli is True
