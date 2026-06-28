# -*- coding: utf-8 -*-
"""tests/test_adaptif_ogrenme.py — AdaptifOgrenme modulu testleri."""

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from adaptif_ogrenme import AdaptifOgrenme, MAKS_TERCIH


class TestAdaptifOgrenmeOlusturma:
    def test_olusturma_varsayilan(self):
        with tempfile.TemporaryDirectory() as tmp:
            ao = AdaptifOgrenme(tercih_dosyasi=os.path.join(tmp, "tercih.json"))
            assert ao is not None

    def test_olusturma_ozel_dosya(self):
        with tempfile.TemporaryDirectory() as tmp:
            dosya = os.path.join(tmp, "alt_dizin", "tercih.json")
            ao = AdaptifOgrenme(tercih_dosyasi=dosya)
            assert Path(dosya).parent.exists()

    def test_basta_bos_tercih(self):
        with tempfile.TemporaryDirectory() as tmp:
            ao = AdaptifOgrenme(tercih_dosyasi=os.path.join(tmp, "t.json"))
            assert ao.tercih_sayisi() == 0

    def test_tum_tercihler_bos_liste(self):
        with tempfile.TemporaryDirectory() as tmp:
            ao = AdaptifOgrenme(tercih_dosyasi=os.path.join(tmp, "t.json"))
            assert ao.tum_tercihler() == []


class TestTercihEkle:
    def _ao(self, tmp):
        return AdaptifOgrenme(tercih_dosyasi=os.path.join(tmp, "t.json"))

    def test_tercih_ekle_basarili(self):
        with tempfile.TemporaryDirectory() as tmp:
            ao = self._ao(tmp)
            sonuc = ao.tercih_ekle("Dosyalari her zaman UTF-8 yaz")
            assert sonuc is True
            assert ao.tercih_sayisi() == 1

    def test_tercih_ekle_duplikat_reddedilir(self):
        with tempfile.TemporaryDirectory() as tmp:
            ao = self._ao(tmp)
            ao.tercih_ekle("Ayni metin")
            sonuc = ao.tercih_ekle("Ayni metin")
            assert sonuc is False
            assert ao.tercih_sayisi() == 1

    def test_tercih_ekle_bos_metin(self):
        with tempfile.TemporaryDirectory() as tmp:
            ao = self._ao(tmp)
            sonuc = ao.tercih_ekle("")
            assert sonuc is False
            assert ao.tercih_sayisi() == 0

    def test_tercih_ekle_sadece_bosluk(self):
        with tempfile.TemporaryDirectory() as tmp:
            ao = self._ao(tmp)
            sonuc = ao.tercih_ekle("   ")
            assert sonuc is False

    def test_tercih_ekle_kaynak_parametresi(self):
        with tempfile.TemporaryDirectory() as tmp:
            ao = self._ao(tmp)
            ao.tercih_ekle("Tercih metni", kaynak="test_kaynak")
            tercihler = ao.tum_tercihler()
            assert tercihler[0]["kaynak"] == "test_kaynak"

    def test_tercih_ekle_uzun_metin_kisaltilir(self):
        with tempfile.TemporaryDirectory() as tmp:
            ao = self._ao(tmp)
            uzun = "X" * 500
            ao.tercih_ekle(uzun)
            tercih = ao.tum_tercihler()[0]
            assert len(tercih["metin"]) <= 300

    def test_tercih_kapasite_siniri(self):
        with tempfile.TemporaryDirectory() as tmp:
            ao = self._ao(tmp)
            for i in range(MAKS_TERCIH + 10):
                ao.tercih_ekle(f"Tercih {i}")
            assert ao.tercih_sayisi() <= MAKS_TERCIH

    def test_tercih_kalici_kaydedilir(self):
        with tempfile.TemporaryDirectory() as tmp:
            dosya = os.path.join(tmp, "t.json")
            ao = AdaptifOgrenme(tercih_dosyasi=dosya)
            ao.tercih_ekle("Kalici tercih")
            # Yeni ornek ayni dosyadan yukleme yaptiginda tercihi gormeli
            ao2 = AdaptifOgrenme(tercih_dosyasi=dosya)
            assert ao2.tercih_sayisi() == 1

    def test_tercih_json_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            dosya = os.path.join(tmp, "t.json")
            ao = AdaptifOgrenme(tercih_dosyasi=dosya)
            ao.tercih_ekle("Format testi")
            icerik = json.loads(Path(dosya).read_text(encoding="utf-8"))
            assert isinstance(icerik, list)
            assert "metin" in icerik[0]
            assert "kaynak" in icerik[0]
            assert "zaman" in icerik[0]


class TestKullaniciMesajiIsle:
    def _ao(self, tmp):
        return AdaptifOgrenme(tercih_dosyasi=os.path.join(tmp, "t.json"))

    def test_duzeltme_sinyali_hayir(self):
        with tempfile.TemporaryDirectory() as tmp:
            ao = self._ao(tmp)
            sonuc = ao.kullanici_mesaji_isle("hayir, boyle yapma")
            assert sonuc is True

    def test_duzeltme_sinyali_yapma(self):
        with tempfile.TemporaryDirectory() as tmp:
            ao = self._ao(tmp)
            sonuc = ao.kullanici_mesaji_isle("bunu yapma lutfen")
            assert sonuc is True

    def test_duzeltme_sinyali_hatirla(self):
        with tempfile.TemporaryDirectory() as tmp:
            ao = self._ao(tmp)
            sonuc = ao.kullanici_mesaji_isle("hatirla: encoding UTF-8 kullan")
            assert sonuc is True

    def test_duzeltme_sinyali_her_zaman(self):
        with tempfile.TemporaryDirectory() as tmp:
            ao = self._ao(tmp)
            sonuc = ao.kullanici_mesaji_isle("her zaman utf-8 kullan")
            assert sonuc is True

    def test_normal_mesaj_kaydedilmez(self):
        with tempfile.TemporaryDirectory() as tmp:
            ao = self._ao(tmp)
            sonuc = ao.kullanici_mesaji_isle("Dosyayi ac ve oku")
            assert sonuc is False
            assert ao.tercih_sayisi() == 0

    def test_normal_soru_kaydedilmez(self):
        with tempfile.TemporaryDirectory() as tmp:
            ao = self._ao(tmp)
            sonuc = ao.kullanici_mesaji_isle("Bu nedir?")
            assert sonuc is False

    def test_kaynak_kullanici_duzeltme(self):
        with tempfile.TemporaryDirectory() as tmp:
            ao = self._ao(tmp)
            ao.kullanici_mesaji_isle("hayir, bunu yapma")
            tercih = ao.tum_tercihler()[0]
            assert tercih["kaynak"] == "kullanici_duzeltme"


class TestTercihBlogu:
    def _ao(self, tmp):
        return AdaptifOgrenme(tercih_dosyasi=os.path.join(tmp, "t.json"))

    def test_blok_bos_yoksa(self):
        with tempfile.TemporaryDirectory() as tmp:
            ao = self._ao(tmp)
            blok = ao.tercih_blogu_al()
            assert blok == ""

    def test_blok_tercih_varsa_dolu(self):
        with tempfile.TemporaryDirectory() as tmp:
            ao = self._ao(tmp)
            ao.tercih_ekle("UTF-8 kullan")
            blok = ao.tercih_blogu_al()
            assert len(blok) > 0
            assert "UTF-8 kullan" in blok

    def test_blok_baslik_iceriyor(self):
        with tempfile.TemporaryDirectory() as tmp:
            ao = self._ao(tmp)
            ao.tercih_ekle("Test tercihi")
            blok = ao.tercih_blogu_al()
            assert "KULLANICI" in blok

    def test_blok_limit_parametresi(self):
        with tempfile.TemporaryDirectory() as tmp:
            ao = self._ao(tmp)
            for i in range(20):
                ao.tercih_ekle(f"Tercih numara {i}")
            blok = ao.tercih_blogu_al(limit=5)
            # En fazla 5 tercih olmali
            sayi = blok.count("\n- ")
            assert sayi <= 5


class TestTercihYonetimi:
    def _ao(self, tmp):
        return AdaptifOgrenme(tercih_dosyasi=os.path.join(tmp, "t.json"))

    def test_tercih_sil_gecerli_indeks(self):
        with tempfile.TemporaryDirectory() as tmp:
            ao = self._ao(tmp)
            ao.tercih_ekle("Silinecek tercih")
            sonuc = ao.tercih_sil(0)
            assert sonuc is True
            assert ao.tercih_sayisi() == 0

    def test_tercih_sil_gecersiz_indeks(self):
        with tempfile.TemporaryDirectory() as tmp:
            ao = self._ao(tmp)
            ao.tercih_ekle("Var olan tercih")
            sonuc = ao.tercih_sil(99)
            assert sonuc is False
            assert ao.tercih_sayisi() == 1

    def test_tercihleri_temizle(self):
        with tempfile.TemporaryDirectory() as tmp:
            ao = self._ao(tmp)
            ao.tercih_ekle("Bir")
            ao.tercih_ekle("Iki")
            ao.tercihleri_temizle()
            assert ao.tercih_sayisi() == 0

    def test_temizle_sonra_dosya_bos(self):
        with tempfile.TemporaryDirectory() as tmp:
            dosya = os.path.join(tmp, "t.json")
            ao = AdaptifOgrenme(tercih_dosyasi=dosya)
            ao.tercih_ekle("Silinecek")
            ao.tercihleri_temizle()
            icerik = json.loads(Path(dosya).read_text(encoding="utf-8"))
            assert icerik == []


class TestSelfCorrection:
    def _ao(self, tmp):
        return AdaptifOgrenme(tercih_dosyasi=os.path.join(tmp, "t.json"))

    def test_python_duzelt_basarili_kod(self):
        """Hatasiz kodun ilk denemede donmesi."""
        with tempfile.TemporaryDirectory() as tmp:
            ao = self._ao(tmp)

            class MockMotor:
                def calistir(self, arac, param):
                    return "42"  # Hatasiz sonuc

            sonuc = ao.python_duzelt_ve_calistir("print(42)", MockMotor(), max_deneme=2)
            assert sonuc == "42"

    def test_python_duzelt_hata_provider_yok(self):
        """Provider olmadan hata kodunu aynen dondurur."""
        with tempfile.TemporaryDirectory() as tmp:
            ao = self._ao(tmp)

            class MockMotor:
                def calistir(self, arac, param):
                    return "[Hata] SyntaxError: invalid syntax"

            sonuc = ao.python_duzelt_ve_calistir(
                "def bozuk(", MockMotor(), provider=None, max_deneme=2
            )
            assert "[Hata]" in sonuc or "Error" in sonuc

    def test_python_duzelt_max_deneme_siniri(self):
        """max_deneme=0 ise hata aninda dur."""
        with tempfile.TemporaryDirectory() as tmp:
            ao = self._ao(tmp)

            cagri_sayisi = {"n": 0}

            class MockMotor:
                def calistir(self, arac, param):
                    cagri_sayisi["n"] += 1
                    return "[Hata] RuntimeError: test"

            ao.python_duzelt_ve_calistir("bozuk_kod", MockMotor(), max_deneme=0)
            assert cagri_sayisi["n"] == 1  # Sadece bir deneme

    def test_python_duzelt_provider_duzeltme_yapar(self):
        """Provider ile duzeltme sonrasi basarili calisma."""
        with tempfile.TemporaryDirectory() as tmp:
            ao = self._ao(tmp)

            deneme = {"n": 0}

            class MockMotor:
                def calistir(self, arac, param):
                    deneme["n"] += 1
                    if deneme["n"] == 1:
                        return "[Hata] NameError: 'x' is not defined"
                    return "Basarili cikti"

            class MockProvider:
                def uret(self, sistem, mesajlar):
                    return "```python\nx = 1\nprint(x)\n```"

            sonuc = ao.python_duzelt_ve_calistir(
                "print(x)", MockMotor(), provider=MockProvider(), max_deneme=2
            )
            assert sonuc == "Basarili cikti"
            assert deneme["n"] == 2
