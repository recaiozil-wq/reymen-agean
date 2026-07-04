# -*- coding: utf-8 -*-
"""test_anayasa_denetci.py — AnayasaDenetci sınıfı için pytest testleri."""

import os
import sys
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

_proje_koku = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _proje_koku not in sys.path:
    sys.path.insert(0, _proje_koku)

from anayasa_denetci import (
    AnayasaDenetci,
    ANAYASAL_ILKELER,
    _ELESTIRI_SISTEM,
    _REVIZYON_SISTEM,
)


# ══════════════════════════════════════════════════════════════════════════
# Fixture'lar
# ══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_provider():
    """Sahte provider — ihlal olmadığını söyler."""
    p = MagicMock()
    p.uret.return_value = (
        "IHLAL_VAR: hayir\n"
        "IHLAL_EDILEN_ILKE: yok\n"
        "KISA_ELESTIRI: Tum ilkeler karsilandi."
    )
    return p


@pytest.fixture
def mock_provider_ihlal():
    """Sahte provider — ihlal olduğunu söyler."""
    p = MagicMock()
    p.uret.return_value = (
        "IHLAL_VAR: evet\n"
        "IHLAL_EDILEN_ILKE: 2. Zarar vermeme\n"
        "KISA_ELESTIRI: rm -rf komutu zararli."
    )
    return p


@pytest.fixture
def denetci(mock_provider):
    return AnayasaDenetci(provider=mock_provider)


@pytest.fixture
def denetci_ihlal(mock_provider_ihlal):
    return AnayasaDenetci(provider=mock_provider_ihlal)


# ══════════════════════════════════════════════════════════════════════════
# Başlatma testleri (1-5)
# ══════════════════════════════════════════════════════════════════════════


class TestBaslatma:
    def test_varsayilan_ilkeler(self):
        """Varsayılan anayasal ilkeler atanmalı."""
        ad = AnayasaDenetci()
        assert len(ad._ilkeler) == 10
        assert ad._ilkeler == list(ANAYASAL_ILKELER)

    def test_ozel_ilkeler(self):
        """Özel ilkeler atanabilmeli."""
        ozel = ["İlke 1: Test", "İlke 2: Test"]
        ad = AnayasaDenetci(ilkeler=ozel)
        assert ad._ilkeler == ozel

    def test_aktif_varsayilan(self):
        """Varsayılan olarak aktif=True olmalı."""
        ad = AnayasaDenetci()
        assert ad.aktif is True

    def test_aktif_false_ise_denetleme_yapilmaz(self, mock_provider):
        """aktif=False ise denetleme direkt geçmeli, LLM çağrılmamalı."""
        ad = AnayasaDenetci(provider=mock_provider, aktif=False)
        onay, sonuc = ad.denetle("tehlikeli hedef", "rm -rf /")
        assert onay is True
        assert sonuc == "rm -rf /"
        mock_provider.uret.assert_not_called()

    def test_provider_yoksa_gecer(self):
        """Provider yoksa (None) denetleme direkt geçmeli."""
        ad = AnayasaDenetci(provider=None)
        onay, sonuc = ad.denetle("test", "cevap")
        assert onay is True
        assert sonuc == "cevap"

    def test_istatistik_sifir(self):
        """Başlangıçta istatistikler sıfır olmalı."""
        ad = AnayasaDenetci()
        stats = ad.istatistik()
        assert stats["elestiri_sayisi"] == 0
        assert stats["revizyon_sayisi"] == 0
        assert stats["revizyon_orani"] == 0.0


# ══════════════════════════════════════════════════════════════════════════
# _basit_soru_mu testleri (6-9)
# ══════════════════════════════════════════════════════════════════════════


class TestBasitSoruMu:
    def test_selam_basit_soru(self):
        """'merhaba' basit soru olarak algılanmalı."""
        assert AnayasaDenetci._basit_soru_mu("merhaba")

    def test_tesekkur_basit_soru(self):
        """'teşekkürler' basit soru olarak algılanmalı."""
        assert AnayasaDenetci._basit_soru_mu("teşekkürler")

    def test_karmaşik_soru_basit_degil(self):
        """Uzun ve karmaşık hedef basit soru sayılmamalı."""
        assert not AnayasaDenetci._basit_soru_mu(
            "Bu projede yer alan tüm dosyaların içeriğini analiz et ve raporla."
        )

    def test_bos_hedef_false(self):
        """Boş hedef için False dönmeli."""
        assert not AnayasaDenetci._basit_soru_mu("")
        assert not AnayasaDenetci._basit_soru_mu(None)

    def test_kisa_ama_basit_olmayan(self):
        """Kısa ama basit kalıp içermeyen hedef False dönmeli."""
        assert not AnayasaDenetci._basit_soru_mu("xyz")


# ══════════════════════════════════════════════════════════════════════════
# denetle testleri (10-16)
# ══════════════════════════════════════════════════════════════════════════


class TestDenetle:
    def test_guvenli_cevap_gecer(self, denetci):
        """Güvenli cevap denetimden geçmeli."""
        onay, sonuc = denetci.denetle("Dosyaları listele", "ls -la ile listelendi.")
        assert onay is True
        assert sonuc == "ls -la ile listelendi."

    def test_basit_soru_direkt_gecer(self, denetci):
        """Basit soru (selam) direkt geçmeli, LLM çağrılmamalı."""
        onay, sonuc = denetci.denetle("merhaba", "Merhaba!")
        assert onay is True
        denetci._provider.uret.assert_not_called()

    def test_ihlal_tespit_edilir(self, denetci_ihlal):
        """İhlal tespit edilince onay=False dönmeli."""
        onay, sonuc = denetci_ihlal.denetle("Dosyaları temizle", "rm -rf /tmp/*")
        assert onay is False

    def test_ihlal_revize_edilir(self, mock_provider_ihlal):
        """İhlal tespit edilince revize edilmeli ve revizyon sayısı artmalı."""
        mock_provider_ihlal.uret.side_effect = [
            # İlk çağrı: elestiri
            "IHLAL_VAR: evet\nIHLAL_EDILEN_ILKE: 2. Zarar\nKISA_ELESTIRI: Zararli.",
            # İkinci çağrı: revizyon
            "Revize edilmis: Dosyalari yedekle.",
        ]
        ad = AnayasaDenetci(provider=mock_provider_ihlal)
        onay, sonuc = ad.denetle("Dosyaları temizle", "rm -rf /tmp/*")
        assert onay is False
        assert "Revize" in sonuc
        assert ad._revizyon_sayisi == 1

    def test_elestiri_sayisi_artar(self, denetci):
        """Her denetleme çağrısında elestiri_sayisi artmalı."""
        denetci.denetle("Hedef", "Cevap")
        assert denetci._elestiri_sayisi == 1
        denetci.denetle("Hedef2", "Cevap2")
        assert denetci._elestiri_sayisi == 2

    def test_ihlal_revize_etme_devre_disiyken(self, mock_provider_ihlal):
        """revize_et=False iken ihlalde revizyon yapılmamalı, uyarı dönmeli."""
        mock_provider_ihlal.uret.return_value = "IHLAL_VAR: evet\nIHLAL_EDILEN_ILKE: 2. Zarar\nKISA_ELESTIRI: Zararli icerik."
        ad = AnayasaDenetci(provider=mock_provider_ihlal)
        onay, sonuc = ad.denetle("Hedef", "Tehlikeli kod", revize_et=False)
        assert onay is False
        assert "[Anayasa Uyarisi]" in sonuc
        assert ad._revizyon_sayisi == 0

    def test_llm_hatasi_sessizce_gecer(self, mock_provider):
        """LLM hatasında ihlal yok sayılmalı."""
        mock_provider.uret.side_effect = Exception("Bağlantı hatası")
        ad = AnayasaDenetci(provider=mock_provider)
        onay, sonuc = ad.denetle("Hedef", "Cevap")
        assert onay is True
        assert sonuc == "Cevap"


# ══════════════════════════════════════════════════════════════════════════
# hizli_kontrol testleri (17-21)
# ══════════════════════════════════════════════════════════════════════════


class TestHizliKontrol:
    def test_rm_rf_yakalanir(self):
        """rm -rf tespit edilmeli."""
        ad = AnayasaDenetci()
        guvenli, uyari = ad.hizli_kontrol("rm -rf /important/files")
        assert guvenli is False
        assert "rm -rf" in uyari

    def test_format_yakalanir(self):
        """format C: tespit edilmeli."""
        ad = AnayasaDenetci()
        guvenli, uyari = ad.hizli_kontrol("format C: /fs:NTFS")
        assert guvenli is False

    def test_drop_table_yakalanir(self):
        """DROP TABLE tespit edilmeli."""
        ad = AnayasaDenetci()
        guvenli, uyari = ad.hizli_kontrol("DROP TABLE users;")
        assert guvenli is False

    def test_os_system_yakalanir(self):
        """os.system('...') tespit edilmeli."""
        ad = AnayasaDenetci()
        guvenli, uyari = ad.hizli_kontrol('os.system("rm -rf /")')
        assert guvenli is False

    def test_guvenli_kod_gecer(self):
        """Güvenli kod hızlı kontrolden geçmeli."""
        ad = AnayasaDenetci()
        guvenli, uyari = ad.hizli_kontrol("print('Merhaba Dünya')")
        assert guvenli is True
        assert uyari == ""


# ══════════════════════════════════════════════════════════════════════════
# istatistik testleri (22-23)
# ══════════════════════════════════════════════════════════════════════════


class TestIstatistik:
    def test_revizyon_orani_hesaplanir(self, mock_provider_ihlal):
        """Revizyon oranı doğru hesaplanmalı."""
        mock_provider_ihlal.uret.side_effect = [
            "IHLAL_VAR: evet\nIHLAL_EDILEN_ILKE: X\nKISA_ELESTIRI: Ihlal.",
            "Revize edilmis cevap.",
        ]
        ad = AnayasaDenetci(provider=mock_provider_ihlal)
        ad.denetle("Hedef", "Kötü cevap")
        stats = ad.istatistik()
        assert stats["elestiri_sayisi"] == 1
        assert stats["revizyon_sayisi"] == 1
        assert stats["revizyon_orani"] == 1.0

    def test_revizyon_orani_sifir(self, denetci):
        """İhlal yoksa revizyon oranı 0 olmalı."""
        denetci.denetle("Hedef", "Guvenli cevap")
        stats = denetci.istatistik()
        assert stats["revizyon_orani"] == 0.0


# ══════════════════════════════════════════════════════════════════════════
# _yanit_ayristir testleri (24-27)
# ══════════════════════════════════════════════════════════════════════════


class TestYanitAyristir:
    def test_ihlal_var_evet_ayristirilir(self):
        """IHLAL_VAR: evet içeren yanıt doğru ayrıştırılmalı."""
        yanit = "IHLAL_VAR: evet\nIHLAL_EDILEN_ILKE: 1. Doğruluk\nKISA_ELESTIRI: Uydurma bilgi."
        sonuc = AnayasaDenetci._yanit_ayristir(yanit)
        assert sonuc["ihlal_var"] is True
        assert "Doğruluk" in sonuc["ihlal_edilen"]
        assert "Uydurma" in sonuc["kisa_elestiri"]

    def test_ihlal_var_hayir_ayristirilir(self):
        """IHLAL_VAR: hayir içeren yanıt doğru ayrıştırılmalı."""
        yanit = "IHLAL_VAR: hayir\nIHLAL_EDILEN_ILKE: yok\nKISA_ELESTIRI: Tum ilkeler karsilandi."
        sonuc = AnayasaDenetci._yanit_ayristir(yanit)
        assert sonuc["ihlal_var"] is False

    def test_case_insensitive_eslesme(self):
        """Büyük/küçük harf duyarsız eşleşme çalışmalı."""
        yanit = "ihlal_var: EVET\nıhlal_edılen_ılke: 5. Verimlilik\nkısa_eleştiri: Gereksiz adım."
        sonuc = AnayasaDenetci._yanit_ayristir(yanit)
        assert sonuc["ihlal_var"] is True

    def test_eksik_alanlar_bos_doner(self):
        """Eksik alanlar boş string dönmeli."""
        yanit = "IHLAL_VAR: evet"
        sonuc = AnayasaDenetci._yanit_ayristir(yanit)
        assert sonuc["ihlal_var"] is True
        assert sonuc["ihlal_edilen"] == ""
        assert sonuc["kisa_elestiri"] == ""


# ══════════════════════════════════════════════════════════════════════════
# _elestir / _revize_et testleri (28-30)
# ══════════════════════════════════════════════════════════════════════════


class TestElestirRevize:
    def test_elestir_cagrisi(self, denetci):
        """_elestir LLM çağrısı yapıp sonucu ayrıştırmalı."""
        sonuc = denetci._elestir("Hedef", "Cevap", [])
        assert isinstance(sonuc, dict)
        assert "ihlal_var" in sonuc
        denetci._provider.uret.assert_called_once()

    def test_revize_et_cagrisi(self, mock_provider_ihlal):
        """_revize_et LLM çağrısı yapıp revize metnini dönmeli."""
        mock_provider_ihlal.uret.return_value = "Revize edilmis cevap."
        ad = AnayasaDenetci(provider=mock_provider_ihlal)
        elestiri = {
            "ihlal_var": True,
            "ihlal_edilen": "1. Doğruluk",
            "kisa_elestiri": "Uydurma.",
        }
        sonuc = ad._revize_et("Hedef", "Eski cevap", elestiri)
        assert sonuc == "Revize edilmis cevap."

    def test_revize_et_hata_durumu(self, mock_provider_ihlal):
        """_revize_et hata alırsa boş string dönmeli."""
        mock_provider_ihlal.uret.side_effect = Exception("API hatası")
        ad = AnayasaDenetci(provider=mock_provider_ihlal)
        elestiri = {"ihlal_var": True, "ihlal_edilen": "X", "kisa_elestiri": "Y"}
        sonuc = ad._revize_et("Hedef", "Cevap", elestiri)
        assert sonuc == ""


# ══════════════════════════════════════════════════════════════════════════
# Sabitler ve prompt formatı (31-32)
# ══════════════════════════════════════════════════════════════════════════


class TestSabitler:
    def test_anayasal_ilkeler_10_adet(self):
        assert len(ANAYASAL_ILKELER) == 10

    def test_elestiri_sistemi_formatlanabilir(self):
        """_ELESTIRI_SISTEM {ilkeler} placeholder'ı içermeli."""
        assert "{ilkeler}" in _ELESTIRI_SISTEM

    def test_revizyon_sistemi_formatlanabilir(self):
        assert "elestiri" in _REVIZYON_SISTEM.lower()
