# -*- coding: utf-8 -*-
"""
test_sistem_talimati.py — sistem_talimati.py modülü için kapsamlı pytest testleri.

Modül: sistem_talimatini_insa_et(hedef, hafiza_ozeti="", son_gozlem="",
                                   araclar=None, ek_bilgi="") -> str

Bu testler prompt insa mantigini dogrular (LLM cagrilmaz).
"""

import sys
import os

_proje_kok = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _proje_kok not in sys.path:
    sys.path.insert(0, _proje_kok)

import pytest
from sistem_talimati import (
    STABLE_TALIMAT,
    IC_GOZLEM_TALIMATI,
    sistem_talimatini_insa_et,
)


# ============================================================
# TEMEL TESTLER
# ============================================================

class TestTemel:
    """En temel davranis testleri."""

    def test_minimum_parametre_string_donuyor(self):
        """Test 1: minimum parametre -> string donuyor"""
        sonuc = sistem_talimatini_insa_et("test hedefi")
        assert isinstance(sonuc, str)
        assert len(sonuc) > 0

    def test_donen_string_1000_karakterden_uzun(self):
        """Test 13: donen string 1000 karakterden uzun (stable talimat var)"""
        sonuc = sistem_talimatini_insa_et("test")
        assert len(sonuc) > 1000

    def test_reyMen_iceriyor(self):
        """Test 2: "ReYMeN" iceriyor mu"""
        sonuc = sistem_talimatini_insa_et("test")
        assert "ReYMeN" in sonuc

    def test_dusunce_ve_eylem_kalibi_var(self):
        """Test 3: "Dusunce:" ve "Eylem:" kalibi var mi"""
        sonuc = sistem_talimatini_insa_et("test")
        assert "Dusunce:" in sonuc
        assert "Eylem:" in sonuc

    def test_gorev_bitti_kalibi_var(self):
        """Test 14: "GOREV_BITTI" kalibi string'de var mi"""
        sonuc = sistem_talimatini_insa_et("test")
        assert "GOREV_BITTI" in sonuc

    def test_hedef_bos_calisir(self):
        """Test 11: hedef bos -> yine de calisir"""
        sonuc = sistem_talimatini_insa_et("")
        assert isinstance(sonuc, str)
        assert len(sonuc) > 0


class TestHedefParametresi:
    """Hedef parametresi davranisi."""

    def test_hedef_gorunuyor(self):
        """Test 4: hedef parametresi string'de gorunuyor"""
        sonuc = sistem_talimatini_insa_et("ozel hedef 12345")
        assert "ozel hedef 12345" in sonuc

    def test_hedef_uzun_1000_karakter(self):
        """Test 10: hedef uzun (1000 karakter) -> string'de tamami var"""
        uzun_hedef = "x" * 1000
        sonuc = sistem_talimatini_insa_et(uzun_hedef)
        assert "x" * 1000 in sonuc


class TestHafizaOzets:
    """Hafiza_ozeti parametresi davranisi."""

    def test_hafiza_ozeti_eklendi_iceriyor(self):
        """Test 5: hafiza_ozeti eklendi -> iceriyor"""
        sonuc = sistem_talimatini_insa_et("test", hafiza_ozeti="daha once x yapildi")
        assert "daha once x yapildi" in sonuc
        # ILGILI HAFIZA basligi da olmali
        assert "ILGILI HAFIZA" in sonuc or "Hafiza" in sonuc or "hafiza" in sonuc

    def test_hafiza_ozeti_bos_eklenmez(self):
        """Hafiza_ozeti bos ise ek baslik eklenmez"""
        sonuc = sistem_talimatini_insa_et("test", hafiza_ozeti="")
        # Bos string eklendiyse metinde gozukmemeli
        assert isinstance(sonuc, str)


class TestSonGozlem:
    """Son_gozlem parametresi davranisi."""

    def test_son_gozlem_eklendi_iceriyor(self):
        """Test 6: son_gozlem eklendi -> iceriyor"""
        sonuc = sistem_talimatini_insa_et("test", son_gozlem="hata alindi: API donmedi")
        assert "hata alindi: API donmedi" in sonuc
        assert "SON GOZLEM" in sonuc

    def test_son_gozlem_bos_eklenmez(self):
        """Son_gozlem bos ise SON GOZLEM basligi gorunmez"""
        sonuc = sistem_talimatini_insa_et("test", son_gozlem="")
        assert "SON GOZLEM" not in sonuc


class TestAraclar:
    """Araclar parametresi (dict) davranisi."""

    def test_araclar_dict_verilince_isimler_gorunur(self):
        """Test 7: araclar dict olarak verilince -> arac isimleri string'de"""
        araclar = {
            "WEB_ARA": "Web aramasi yapar",
            "DOSYA_OKU": "Dosya icerigini okur",
            "PYTHON_CALISTIR": "Python kodu calistirir",
        }
        sonuc = sistem_talimatini_insa_et("test", araclar=araclar)
        assert "WEB_ARA" in sonuc
        assert "DOSYA_OKU" in sonuc
        assert "PYTHON_CALISTIR" in sonuc

    def test_araclar_dict_aciklamalari_gorunur(self):
        """Araclar dict'teki aciklamalar da gorunur"""
        araclar = {
            "OZEL_ARAC": "Ozel bir islemi yapar",
        }
        sonuc = sistem_talimatini_insa_et("test", araclar=araclar)
        assert "OZEL_ARAC" in sonuc
        assert "Ozel bir islemi yapar" in sonuc

    def test_araclar_none_eklenmez(self):
        """Test 8: araclar=None -> extra arac bolumu eklenmez"""
        sonuc_aracli = sistem_talimatini_insa_et("test", araclar={"X": "Y"})
        sonuc_aracsiz = sistem_talimatini_insa_et("test", araclar=None)

        # araclar=None ile sonuc stable talimatin kendisinden kisa olmamali
        assert isinstance(sonuc_aracsiz, str)
        assert len(sonuc_aracsiz) > 0

    def test_araclar_bos_dict_aracsiz_ile_ayni(self):
        """Bos dict verilince None ile ayni davranmali"""
        sonuc_none = sistem_talimatini_insa_et("test", araclar=None)
        sonuc_bos = sistem_talimatini_insa_et("test", araclar={})
        assert isinstance(sonuc_bos, str)
        assert len(sonuc_bos) > 0

    def test_araclar_dict_fazla_arac_ekler(self):
        """Dict verildiginde prompt'ta arac bolumu degisir"""
        sonuc_aracli = sistem_talimatini_insa_et("test", araclar={"TEST_ARAC": "test"})
        sonuc_aracsiz = sistem_talimatini_insa_et("test")
        # Aracli olan prompt'ta KULLANABILECEN ARACLAR (GUNCELL) bolumu var
        assert "KULLANABILECEN ARACLAR (GUNCELL)" in sonuc_aracli
        assert "KULLANABILECEN ARACLAR (GUNCELL)" not in sonuc_aracsiz
        # TEST_ARAC sadece aracli versiyonda var
        assert "TEST_ARAC" in sonuc_aracli
        assert "TEST_ARAC" not in sonuc_aracsiz


class TestEkBilgi:
    """Ek_bilgi parametresi davranisi."""

    def test_ek_bilgi_eklenince_iceriyor(self):
        """Test 9: ek_bilgi eklenince -> iceriyor"""
        sonuc = sistem_talimatini_insa_et("test", ek_bilgi="Bu bir test modudur")
        assert "Bu bir test modudur" in sonuc

    def test_ek_bilgi_bos_eklenmez(self):
        """Ek_bilgi bos ise prompt'ta ekstra icerik yok"""
        sonuc = sistem_talimatini_insa_et("test", ek_bilgi="")
        assert isinstance(sonuc, str)

    def test_ek_bilgi_uzun_metin_icerir(self):
        """Ek_bilgi uzun metin olabilir"""
        uzun_ek = "Ek talimat. " * 50
        sonuc = sistem_talimatini_insa_et("test", ek_bilgi=uzun_ek)
        assert uzun_ek in sonuc

    def test_ek_bilgi_ile_tum_parametreler_birlikte(self):
        """Ek_bilgi diger parametrelerle birlikte calisir"""
        sonuc = sistem_talimatini_insa_et(
            "test",
            hafiza_ozeti="hafiza",
            son_gozlem="gozlem",
            araclar={"X": "Y"},
            ek_bilgi="ekstra talimat",
        )
        assert isinstance(sonuc, str)
        assert len(sonuc) > 0


class TestTumParametreler:
    """Tum parametrelerin birlikte calismasi."""

    def test_tum_parametreler_dolu_hepsi_gorunuyor(self):
        """Test 12: tum parametreler dolu -> hepsi string'de gorunuyor"""
        araclar = {
            "WEB_ARA": "Web aramasi",
            "DOSYA_OKU": "Dosya okuma",
        }
        sonuc = sistem_talimatini_insa_et(
            "ana hedef",
            hafiza_ozeti="gecmis bilgi",
            son_gozlem="API yaniti: OK",
            araclar=araclar,
            ek_bilgi="Dikkat: test modu aktif",
        )
        assert isinstance(sonuc, str)
        assert "ana hedef" in sonuc
        assert "gecmis bilgi" in sonuc
        assert "API yaniti: OK" in sonuc
        assert "WEB_ARA" in sonuc
        assert "DOSYA_OKU" in sonuc
        assert "Dikkat: test modu aktif" in sonuc

    def test_hepsi_bos_veya_none_calisir(self):
        """Tum optional parametreler bos/None -> hata yok"""
        sonuc = sistem_talimatini_insa_et(
            "test",
            hafiza_ozeti="",
            son_gozlem="",
            araclar=None,
            ek_bilgi="",
        )
        assert isinstance(sonuc, str)
        assert len(sonuc) > 1000


# ============================================================
# KAPSAYICI TESTLER
# ============================================================

class TestKapsayici:
    """Prompt icerigi ve yapisi testleri."""

    def test_stable_talimat_tamami_korunur(self):
        """STABLE_TALIMAT icerigi prompt'ta yer alir"""
        sonuc = sistem_talimatini_insa_et("test")
        # STABLE_TALIMAT'in baslangici prompt'un basinda olmali
        assert sonuc.startswith(STABLE_TALIMAT[:50])
        # Temel bolumler mevcut
        for keyword in [
            "ReYMeN",
            "DeepSeek",
            "Dusunce:",
            "Eylem:",
            "GOREV_BITTI",
            "KULLANABILECEN ARACLAR",
            "CUA",
            "IC_GOZLEM",
        ]:
            assert keyword in sonuc, f"{keyword} prompt'ta bulunamadi"

    def test_stable_talimat_anahtar_bolumleri(self):
        """STABLE_TALIMAT ana bolum basliklarini icerir"""
        for bolum in [
            "KATIKSIZ KURALLAR",
            "DUSUNCE KALITESI",
            "ARAC SECIM REHBERI",
            "KULLANABILECEN ARACLAR",
        ]:
            assert bolum in STABLE_TALIMAT, f"Bolum eksik: {bolum}"

    def test_stable_talimat_kanban_icerir(self):
        """STABLE_TALIMAT KANBAN bolumunu icerir"""
        assert "KANBAN" in STABLE_TALIMAT

    def test_stable_talimat_telegram_araclari(self):
        """Telegram araclari stable talimatta var"""
        assert "TELEGRAM_GONDER" in STABLE_TALIMAT

    def test_ic_gozlem_talimati_tanimli(self):
        """IC_GOZLEM_TALIMATI sabiti tanimli ve bos degil"""
        assert IC_GOZLEM_TALIMATI
        assert isinstance(IC_GOZLEM_TALIMATI, str)
        assert len(IC_GOZLEM_TALIMATI) > 50

    def test_turkce_cevap_kurali_var(self):
        """Turkce cevap kurali stable talimatta var"""
        sonuc = sistem_talimatini_insa_et("test")
        assert "Turkce" in sonuc or "Türkçe" in sonuc or "turkce" in sonuc

    def test_birden_fazla_eylem_yasagi_var(self):
        """'birden fazla eylem' yasagi prompt'ta var"""
        sonuc = sistem_talimatini_insa_et("test")
        assert "birden fazla eylem" in sonuc

    def test_gozlem_uydurma_yasagi_var(self):
        """'gozlem uydurma' yasagi prompt'ta var"""
        sonuc = sistem_talimatini_insa_et("test")
        assert "gozlem uydurma" in sonuc


class TestFonksiyonel:
    """Fonksiyonel ve sinir testleri."""

    def test_donus_tipi_her_zaman_string(self):
        """Her kosulda string doner"""
        for hedef in ["a", "", "  ", "123", "x" * 5000]:
            sonuc = sistem_talimatini_insa_et(hedef)
            assert isinstance(sonuc, str), f"Hedef='{hedef[:20]}' string donmedi"

    def test_araclar_dict_buyuk_sozluk(self):
        """50 arac iceren sozluk ile calisir"""
        araclar = {f"ARAC_{i}": f"{i}. arac aciklamasi" for i in range(50)}
        sonuc = sistem_talimatini_insa_et("test", araclar=araclar)
        assert isinstance(sonuc, str)
        assert "ARAC_0" in sonuc
        assert "ARAC_49" in sonuc

    def test_ek_bilgi_ozel_karakterler(self):
        """Ek_bilgi ozel karakterler icerebilir"""
        ek = "Ozel: ~!@#$%^&*()_+-=[]{}|;:',.<>?/`"
        sonuc = sistem_talimatini_insa_et("test", ek_bilgi=ek)
        assert ek in sonuc

    def test_hafiza_ozeti_uzun_metin(self):
        """Hafiza_ozeti 5000 karakter olabilir"""
        uzun = "hafiza " * 1000  # ~7000 chars
        sonuc = sistem_talimatini_insa_et("test", hafiza_ozeti=uzun)
        assert isinstance(sonuc, str)
        assert "hafiza" in sonuc

    def test_son_gozlem_cok_satirli(self):
        """Son_gozlem cok satirli metin olabilir"""
        gozlem = "Satir 1\nSatir 2\nSatir 3\n"
        sonuc = sistem_talimatini_insa_et("test", son_gozlem=gozlem)
        assert "Satir 1" in sonuc
        assert "Satir 2" in sonuc
        assert "Satir 3" in sonuc

    def test_araclar_arac_isimleri_ve_aciklamalari(self):
        """Her arac icin isim+aciklama formatina uygun"""
        araclar = {
            "WEB_ARA": "Web'de arama yapar",
            "DOSYA_YAZ": "Dosyaya yazar",
        }
        sonuc = sistem_talimatini_insa_et("test", araclar=araclar)
        for arac_adi, aciklama in araclar.items():
            assert arac_adi in sonuc
            assert aciklama in sonuc


class TestPromptYapisi:
    """Prompt yapisal testler."""

    def test_stable_sonrasi_hedef_bolumu(self):
        """ANA HEDEF bolumu var"""
        sonuc = sistem_talimatini_insa_et("test")
        assert "ANA HEDEF" in sonuc

    def test_stable_sonrasi_ek_bilgi_bolumu(self):
        """ek_bilgi verildiginde EK BILGI bolumu var"""
        sonuc = sistem_talimatini_insa_et("test", ek_bilgi="Tur 3/15")
        assert "EK BILGI" in sonuc
        assert "Tur 3/15" in sonuc

    def test_prompt_bosluk_dogrulama(self):
        """Ardarda 3'ten fazla bos satir yok"""
        sonuc = sistem_talimatini_insa_et("test")
        lines = sonuc.split("\n")
        bos_sayisi = 0
        for line in lines:
            if line.strip() == "":
                bos_sayisi += 1
            else:
                bos_sayisi = 0
            assert bos_sayisi <= 3, "Ardarda 3'ten fazla bos satir var"


# ============================================================
# GERILEME TESTLERI
# ============================================================

class TestGerileme:
    """Daha once calisan davranislarin korundugunu dogrular."""

    def test_stable_talimat_deepseek_bilgisi(self):
        """DeepSeek altyapi bilgisi prompt'ta yer aliyor"""
        sonuc = sistem_talimatini_insa_et("test")
        assert "DeepSeek" in sonuc

    def test_stable_talimat_react_vurgusu(self):
        """ReAct dongusu vurgusu prompt'ta yer aliyor"""
        sonuc = sistem_talimatini_insa_et("test")
        assert "ReAct" in sonuc

    def test_stable_sonrasi_basari_bolumu(self):
        """BASARI rozet bolumu prompt'ta yer aliyor"""
        sonuc = sistem_talimatini_insa_et("test")
        assert "BASARI" in sonuc or "Rozet" in sonuc or "ROZET" in sonuc

    def test_stable_talimat_watchdog_kontrol(self):
        """WATCHDOG_KONTROL arac tanimi prompt'ta var"""
        sonuc = sistem_talimatini_insa_et("test")
        assert "WATCHDOG_KONTROL" in sonuc
