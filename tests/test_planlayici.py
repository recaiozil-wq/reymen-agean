# -*- coding: utf-8 -*-
"""test_planlayici.py — Planlayici sinifi icin kapsamli pytest testleri (23 test).

Planlayici, bir LLM saglayicisi (provider) kullanan bir planlama moduludur.
Provider unittest.mock.MagicMock ile taklit edilir.
"""

import sys
from pathlib import Path

PROJ_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJ_ROOT))

import pytest
from unittest.mock import MagicMock, patch
from planlayici import (
    Planlayici, PLAN_TALIMATI, YENIDEN_PLAN_TALIMATI,
    TOT_STRATEJI_TALIMATI, TOT_DEGERLENDIRME_TALIMATI,
)


# ── Helpers ────────────────────────────────────────────────────────────────────


def _mock_provider(return_value: str = ""):
    """return_value degerini donen bir provider mock'u olustur."""
    prov = MagicMock()
    prov.uret.return_value = return_value
    return prov


# ═══════════════════════════════════════════════════════════════════════════════
# Test 1: __init__
# ═══════════════════════════════════════════════════════════════════════════════

class TestInit:
    """Planlayici kurulum testleri — Test 1."""

    def test_init_provider_set(self):
        """1: provider dogru sekilde atanmali."""
        prov = MagicMock()
        p = Planlayici(prov)
        assert p.provider is prov

    def test_init_tamamlanan_bos(self):
        """1: baslangicta tamamlanan adim listesi bos olmali."""
        p = Planlayici(MagicMock())
        assert p._tamamlanan == []
        assert p.tamamlananlar() == []


# ═══════════════════════════════════════════════════════════════════════════════
# Test 2-6: plani_uret
# ═══════════════════════════════════════════════════════════════════════════════

class TestPlaniUret:
    """plani_uret() normal (ToTsiz) plan uretme testleri — Test 2-6."""

    def test_plani_uret_normal(self):
        """2: provider mock "1. x\\n2. y\\n3. z" -> ["x", "y", "z"]."""
        prov = _mock_provider("1. x\n2. y\n3. z")
        p = Planlayici(prov)
        sonuc = p.plani_uret("bir web sitesinden veri cek ve analiz et")
        # _satirlari_ayristir numara ve noktayi temizler
        assert sonuc == ["x", "y", "z"]
        prov.uret.assert_called_once()

    def test_plani_uret_tot_true_yonlendirme(self):
        """3: tot=True ile tot_plani_uret cagrilir, 3 farkli cevap -> 3 plan."""
        prov = _mock_provider()
        p = Planlayici(prov)
        # tot_plani_uret'i monte et
        p.tot_plani_uret = MagicMock(return_value=["plan_a", "plan_b", "plan_c"])
        sonuc = p.plani_uret("bir web sitesinden veri cek ve analiz et", tot=True)
        p.tot_plani_uret.assert_called_once_with("bir web sitesinden veri cek ve analiz et")
        assert sonuc == ["plan_a", "plan_b", "plan_c"]

    def test_plani_uret_bos_cevap(self):
        """4: provider bos string dondu -> [hedef] (falsy guard)."""
        prov = _mock_provider("")
        p = Planlayici(prov)
        sonuc = p.plani_uret("test hedefi")
        # _satirlari_ayristir("") -> [], [] or [hedef] -> [hedef]
        assert sonuc == ["test hedefi"]

    def test_plani_uret_none_cevap(self):
        """5: provider None dondu -> AttributeError (try/except disinda)."""
        prov = _mock_provider()
        prov.uret.return_value = None
        p = Planlayici(prov)
        with pytest.raises(AttributeError, match="splitlines"):
            p.plani_uret("bir web sitesinden veri cek ve analiz et")

    def test_plani_uret_provider_hata(self):
        """6: provider hata firlatti -> [hedef]."""
        prov = MagicMock()
        prov.uret.side_effect = RuntimeError("Provider erisilemez")
        p = Planlayici(prov)
        sonuc = p.plani_uret("bir web sitesindeki tum verileri cek ve json dosyasina kaydet")
        assert sonuc == ["bir web sitesindeki tum verileri cek ve json dosyasina kaydet"]

    def test_plani_uret_basit_sorgu_bypass(self):
        """7: Basit sorgular (3 kelime veya az) provider'i cagirmadan direkt doner."""
        prov = MagicMock()
        p = Planlayici(prov)
        # Selamlama
        assert p.plani_uret("merhaba") == ["merhaba"]
        prov.uret.assert_not_called()
        # Kisa soru
        assert p.plani_uret("nasilsin") == ["nasilsin"]
        prov.uret.assert_not_called()
        # 3 kelime
        assert p.plani_uret("bu bir test") == ["bu bir test"]
        prov.uret.assert_not_called()


# ═══════════════════════════════════════════════════════════════════════════════
# Test 8-9, 24: tot_plani_uret ve _tot_yurut
# ═══════════════════════════════════════════════════════════════════════════════

class TestTotPlaniUret:
    """Tree-of-Thought plan uretme testleri — Test 7-8, 23."""

    def test_tot_plani_uret_uc_strateji_secim(self):
        """7: 3 cevap -> 3 elemanli liste (en iyi strateji secilir)."""
        prov = MagicMock()
        prov.uret.side_effect = [
            "1. Strateji1 Adim1\n2. Strateji1 Adim2",
            "1. Strateji2 Adim1\n2. Strateji2 Adim2\n3. Strateji2 Adim3",
            "1. Strateji3 Adim1",
            "En iyi plan: 2",
        ]
        p = Planlayici(prov)
        sonuc = p.tot_plani_uret("test hedefi")
        assert sonuc == ["Strateji2 Adim1", "Strateji2 Adim2", "Strateji2 Adim3"]
        assert prov.uret.call_count == 4

    def test_tot_plani_uret_tek_strateji_direkt_don(self):
        """Sadece 1 strateji uretilebilirse direkt onu doner."""
        prov = MagicMock()
        prov.uret.side_effect = [
            "1. Tek strateji adimi",
            Exception("2. strateji basarisiz"),
            Exception("3. strateji basarisiz"),
        ]
        p = Planlayici(prov)
        sonuc = p.tot_plani_uret("test hedefi")
        assert sonuc == ["Tek strateji adimi"]
        assert prov.uret.call_count == 3

    def test_tot_plani_uret_hic_strateji_yok_fallback(self):
        """Hic strateji uretilemezse fallback plani_uret(tot=False)."""
        prov = MagicMock()
        prov.uret.side_effect = [
            Exception("Hata 1"),
            Exception("Hata 2"),
            Exception("Hata 3"),
        ]
        p = Planlayici(prov)
        with patch.object(p, "plani_uret", return_value=["fallback adim"]) as mock_fb:
            sonuc = p.tot_plani_uret("test hedefi")
            mock_fb.assert_called_once_with("test hedefi", tot=False)
            assert sonuc == ["fallback adim"]

    def test_tot_plani_uret_degerlendirme_basarisiz_en_kisa(self):
        """Degerlendirme basarisiz olursa en kisa strateji secilir."""
        prov = MagicMock()
        prov.uret.side_effect = [
            "1. A1\n2. A2\n3. A3",
            "1. B1",
            "1. C1\n2. C2",
            "Bilinmeyen format",
        ]
        p = Planlayici(prov)
        sonuc = p.tot_plani_uret("test hedefi")
        # En kisa = stratejiB (1 adim)
        assert sonuc == ["B1"]

    def test_tot_plani_uret_hata_yakalama(self):
        """8: provider hata firlatti -> fallback plani_uret."""
        prov = MagicMock()
        prov.uret.side_effect = Exception("Beklenmeyen hata")
        p = Planlayici(prov)
        with patch.object(p, "plani_uret", return_value=["fallback"]) as mock_fb:
            sonuc = p.tot_plani_uret("test hedefi")
            mock_fb.assert_called_once_with("test hedefi", tot=False)
            assert sonuc == ["fallback"]

    def test_tot_plani_uret_iki_strateji_eksik_calisir(self):
        """23 (NEGATIF): tot=True ama provider 2 cevap dondu -> eksik de olsa calisir."""
        prov = MagicMock()
        prov.uret.side_effect = [
            "1. Strateji1 Adim1\n2. Strateji1 Adim2",
            "1. Strateji2 Adim1",
            Exception("3. strateji basarisiz"),
            "En iyi plan: 1",
        ]
        p = Planlayici(prov)
        sonuc = p.tot_plani_uret("test hedefi")
        # 2 strateji basarili, 1. secildi
        assert sonuc == ["Strateji1 Adim1", "Strateji1 Adim2"]
        assert prov.uret.call_count == 4  # 2 basarili + 1 basarisiz + 1 degerlendirme


# ═══════════════════════════════════════════════════════════════════════════════
# Test 9-10: yeniden_planla
# ═══════════════════════════════════════════════════════════════════════════════

class TestYenidenPlanla:
    """Yeniden planlama testleri — Test 9-10."""

    def test_yeniden_planla_basarili(self):
        """9: mock "1. yeni\\n2. yeni2" -> ["yeni", "yeni2"]."""
        prov = _mock_provider("1. yeni\n2. yeni2")
        p = Planlayici(prov)
        sonuc = p.yeniden_planla("test hedefi", ["onceki adim"], "timeout hatasi")
        assert sonuc == ["yeni", "yeni2"]
        prov.uret.assert_called_once()

    def test_yeniden_planla_tamamlanan_adim_stringde(self):
        """10: tamamlanan_adimlar="1.adim" prompt string'inde gorunur."""
        prov = MagicMock()
        prov.uret.return_value = "1. yeni adim"
        p = Planlayici(prov)
        p.yeniden_planla("test", ["1.adim", "2.adim"], "hata")
        cagri_prompt = prov.uret.call_args[0][0]
        assert "- 1.adim" in cagri_prompt
        assert "- 2.adim" in cagri_prompt

    def test_yeniden_planla_tamamlanan_bos(self):
        """Hic adim tamamlanmamissa promptta ibare gorunur."""
        prov = _mock_provider("1. bastan basla")
        p = Planlayici(prov)
        sonuc = p.yeniden_planla("test", [], "hata")
        assert sonuc == ["bastan basla"]
        cagri_prompt = prov.uret.call_args[0][0]
        assert "(hic adim tamamlanmadi)" in cagri_prompt

    def test_yeniden_planla_hata_bos_donus(self):
        """Provider hata firlatirsa [] donmeli."""
        prov = MagicMock()
        prov.uret.side_effect = ConnectionError("Baglanti hatasi")
        p = Planlayici(prov)
        sonuc = p.yeniden_planla("test", ["adim"], "hata")
        assert sonuc == []

    def test_yeniden_planla_hata_mesaji_kisaltma(self):
        """Uzun hata mesaji ilk 300 karaktere kesilmeli."""
        prov = MagicMock()
        prov.uret.return_value = "1. yeni adim"
        p = Planlayici(prov)
        uzun_hata = "X" * 500
        sonuc = p.yeniden_planla("test", ["adim"], uzun_hata)
        assert sonuc == ["yeni adim"]
        cagri_prompt = prov.uret.call_args[0][0]
        assert len(uzun_hata) > 300
        assert "X" * 300 in cagri_prompt
        assert "X" * 301 not in cagri_prompt


# ═══════════════════════════════════════════════════════════════════════════════
# Test 11-13: tamamlanan_adim_isaretle
# ═══════════════════════════════════════════════════════════════════════════════

class TestTamamlananAdimIsaretle:
    """Adim tamamlama isaretleme testleri — Test 11-13."""

    def test_ekle_ve_listele(self):
        """11: "test" ekle -> tamamlananlar() ["test"]."""
        p = Planlayici(MagicMock())
        p.tamamlanan_adim_isaretle("test")
        assert p.tamamlananlar() == ["test"]

    def test_none_ekle_hata_yok(self):
        """12: None ekle -> hata yok (None listeye eklenir)."""
        p = Planlayici(MagicMock())
        p.tamamlanan_adim_isaretle(None)
        # None deger olarak listeye eklenir, hata firlatmaz
        assert p.tamamlananlar() == [None]

    def test_on_kere_ekle_on_eleman(self):
        """13: 10 kere ekle -> 10 eleman."""
        p = Planlayici(MagicMock())
        for i in range(10):
            p.tamamlanan_adim_isaretle(f"adim_{i}")
        assert len(p.tamamlananlar()) == 10
        assert p.tamamlananlar() == [f"adim_{i}" for i in range(10)]


# ═══════════════════════════════════════════════════════════════════════════════
# Test 14: tamamlananlar
# ═══════════════════════════════════════════════════════════════════════════════

class TestTamamlananlar:
    """Tamamlanan adim listesi testleri — Test 14."""

    def test_bos_baslangic(self):
        """14: hic eklenmedi -> []."""
        p = Planlayici(MagicMock())
        assert p.tamamlananlar() == []

    def test_kopya_donmeli(self):
        """Ic liste kopyasini donmeli (ic yapi korunmali)."""
        p = Planlayici(MagicMock())
        p._tamamlanan.append("gizli adim")
        dis_kopya = p.tamamlananlar()
        dis_kopya.append("eklenen")
        assert "eklenen" not in p._tamamlanan


# ═══════════════════════════════════════════════════════════════════════════════
# Test 15-17: riskli_mi
# ═══════════════════════════════════════════════════════════════════════════════

class TestRiskliMi:
    """Risk degerlendirme testleri — Test 15-17."""

    def test_risk_etiketi_icerir(self):
        """15: "[RISK]" iceren -> True."""
        p = Planlayici(MagicMock())
        assert p.riskli_mi("Dosyaya [RISK] yaz") is True

    def test_normal_adim_false(self):
        """16: normal adim -> False."""
        p = Planlayici(MagicMock())
        assert p.riskli_mi("Dosyaya yaz") is False

    def test_risk_kucuk_harf_etiketi_ile_true(self):
        """[risk] kucuk harf etiketi -> True (.upper() sayesinde)."""
        p = Planlayici(MagicMock())
        assert p.riskli_mi("[risk] silme islemi") is True

    def test_risk_kucuk_harf_etiket(self):
        """17: "risk" (etiketsiz, bracketsiz) -> False."""
        p = Planlayici(MagicMock())
        # "risk" yazisi ama [RISK] etiketi yok -> False
        assert p.riskli_mi("Bu islem risk iceriyor") is False

    def test_bos_adim_false(self):
        """Bos adim -> False."""
        p = Planlayici(MagicMock())
        assert p.riskli_mi("") is False


# ═══════════════════════════════════════════════════════════════════════════════
# Test 18: sifirla
# ═══════════════════════════════════════════════════════════════════════════════

class TestSifirla:
    """Sifirlama testleri — Test 18."""

    def test_sifirla_sonrasi_bos(self):
        """18: 3 adim ekle sonra sifirla -> tamamlananlar() [].

        sifirla() tum tamamlanan adim listesini bosaltmali.
        """
        p = Planlayici(MagicMock())
        p.tamamlanan_adim_isaretle("adim 1")
        p.tamamlanan_adim_isaretle("adim 2")
        p.tamamlanan_adim_isaretle("adim 3")
        assert len(p.tamamlananlar()) == 3
        p.sifirla()
        assert p.tamamlananlar() == []


# ═══════════════════════════════════════════════════════════════════════════════
# Test 19-22: _satirlari_ayristir
# ═══════════════════════════════════════════════════════════════════════════════

class TestSatirlariAyristir:
    """_satirlari_ayristir yardimci metot testleri — Test 19-22.

    NOT: _satirlari_ayristir lstrip("0123456789.)- ") ile sayilari,
    noktalari, tireleri ve parantezleri temizler, sadece metin kalir.
    """

    def test_normal_liste(self):
        """19: "1. a\\n2. b\\n3. c" -> ["a", "b", "c"]."""
        p = Planlayici(MagicMock())
        sonuc = p._satirlari_ayristir("1. a\n2. b\n3. c")
        assert sonuc == ["a", "b", "c"]

    def test_tek_adim(self):
        """20: "1. a" -> ["a"]."""
        p = Planlayici(MagicMock())
        sonuc = p._satirlari_ayristir("1. a")
        assert sonuc == ["a"]

    def test_bos_string(self):
        """21: "" -> []."""
        p = Planlayici(MagicMock())
        assert p._satirlari_ayristir("") == []

    def test_bosluklu_cevap(self):
        """22: bosluklu cevap -> strip edilmis."""
        p = Planlayici(MagicMock())
        cevap = "  1. ilk adim   \n  2. ikinci adim  "
        sonuc = p._satirlari_ayristir(cevap)
        assert sonuc == ["ilk adim", "ikinci adim"]

    def test_tire_ile_baslayan(self):
        """Tire (-) ile baslayan satirlar da adim olarak algilanmali."""
        p = Planlayici(MagicMock())
        sonuc = p._satirlari_ayristir("- Ilk adim\n- Ikinci adim")
        assert sonuc == ["Ilk adim", "Ikinci adim"]

    def test_parantezli_numara(self):
        """1) 2) gibi parantezli numaralama."""
        p = Planlayici(MagicMock())
        sonuc = p._satirlari_ayristir("1) Adim bir\n2) Adim iki")
        assert sonuc == ["Adim bir", "Adim iki"]

    def test_cok_basamakli_numara(self):
        """10., 11. gibi cok basamakli."""
        p = Planlayici(MagicMock())
        sonuc = p._satirlari_ayristir("10. onuncu adim\n11. on birinci adim")
        assert sonuc == ["onuncu adim", "on birinci adim"]

    def test_numara_icermeyen_satir_atlanir(self):
        """Numara veya tire ile baslamayan satirlar atlanmali."""
        p = Planlayici(MagicMock())
        cevap = "1. gercek adim\naciklama satiri\n2. ikinci adim"
        sonuc = p._satirlari_ayristir(cevap)
        assert sonuc == ["gercek adim", "ikinci adim"]

    def test_sadece_bos_satir(self):
        """Sadece bosluk iceren satirlar yok sayilmali."""
        p = Planlayici(MagicMock())
        assert p._satirlari_ayristir("   \n  \n") == []


# ═══════════════════════════════════════════════════════════════════════════════
# Ek: sabit metin varlik testleri
# ═══════════════════════════════════════════════════════════════════════════════

class TestSabitMetinler:
    """Modul sabit metinleri ve yapisi."""

    def test_plan_talimati_var(self):
        assert len(PLAN_TALIMATI) > 50
        assert "gorev planlayicisi" in PLAN_TALIMATI.lower()

    def test_yeniden_plan_talimati_format(self):
        assert "{tamamlanan}" in YENIDEN_PLAN_TALIMATI
        assert "{hata}" in YENIDEN_PLAN_TALIMATI
        assert "{kalan_hedef}" in YENIDEN_PLAN_TALIMATI

    def test_tot_strateji_talimati_format(self):
        assert "{numara}" in TOT_STRATEJI_TALIMATI
        assert "{odak}" in TOT_STRATEJI_TALIMATI
        assert "{hedef}" in TOT_STRATEJI_TALIMATI

    def test_tot_degerlendirme_talimati_format(self):
        assert "{strateji_sayisi}" in TOT_DEGERLENDIRME_TALIMATI
        assert "{hedef}" in TOT_DEGERLENDIRME_TALIMATI
        assert "{planlar}" in TOT_DEGERLENDIRME_TALIMATI

    def test_tot_odaklar_uc_adet(self):
        p = Planlayici(MagicMock())
        assert len(p._TOT_ODAKLAR) == 3
        assert "en hizli" in p._TOT_ODAKLAR[0].lower()
        assert "en guvenli" in p._TOT_ODAKLAR[1].lower()
        assert "alternatif" in p._TOT_ODAKLAR[2].lower()
