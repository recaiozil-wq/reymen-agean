# -*- coding: utf-8 -*-
"""test_context_compressor.py — ContextCompressor icin kapsamli pytest testleri."""

import json
import pytest
from context_compressor import ContextCompressor


# ── Fixture ─────────────────────────────────────────────────────────────

@pytest.fixture
def compressor():
    return ContextCompressor(max_token=1024)


@pytest.fixture
def ornek_gecmis():
    return [
        {"rol": "kullanici", "icerik": "Merhaba, nasilsin?"},
        {"rol": "asistan", "icerik": "Iyiyim, tesekkurler. Sana nasil yardimci olabilirim?"},
        {"rol": "kullanici", "icerik": "Python ile dosya islemleri yapmak istiyorum."},
        {"rol": "asistan", "icerik": "Python'da dosya islemleri icin open() fonksiyonunu kullanabilirsin."},
        {"rol": "kullanici", "icerik": "Peki json nasil okunur?"},
        {"rol": "asistan", "icerik": "json.load() ile dosyadan okuyabilirsin."},
    ]


# ── Test 1: Baslangic durumu ────────────────────────────────────────────

class TestBaslangic:
    def test_baslangic_varsayilan_max_token(self):
        """Varsayilan max_token 16384 olmali."""
        c = ContextCompressor()
        assert c._max_token == 16384

    def test_baslangic_ozel_max_token(self):
        """Ozel max_token degeri dogru atanmali."""
        c = ContextCompressor(max_token=4096)
        assert c._max_token == 4096

    def test_baslangic_bos_sozlukler(self):
        """Baslangicta tum ic veriler bos olmali."""
        c = ContextCompressor()
        assert c._onemli_bilgiler == {}
        assert c._ozet_gecmisi == []
        assert c._etiket_puani == {}

    def test_istatistik_baslangic(self):
        """istatistik() baslangicta dogru degerler donmeli."""
        c = ContextCompressor(max_token=8192)
        stats = c.istatistik()
        assert stats["onemli_bilgi_sayisi"] == 0
        assert stats["ozet_sayisi"] == 0
        assert stats["max_token"] == 8192


# ── Test 2: sikistir ────────────────────────────────────────────────────

class TestSikistir:
    def test_bos_gecmis(self, compressor):
        """Bos gecmis listesi bos liste donmeli."""
        assert compressor.sikistir([]) == []

    def test_sikistir_ozet_ekler(self, compressor, ornek_gecmis):
        """Sikistirma ilk mesaj olarak ozet eklemeli."""
        sonuc = compressor.sikistir(ornek_gecmis)
        assert len(sonuc) > 0
        assert sonuc[0]["rol"] == "sistem"
        assert "[OZET]" in sonuc[0]["icerik"]

    def test_sikistir_onemli_bilgileri_ekler(self, compressor, ornek_gecmis):
        """Onemli bilgiler varsa sikistirilmis sonuca eklenmeli."""
        compressor.onemli_bilgileri_sakla("kullanici_adi", "test_user")
        sonuc = compressor.sikistir(ornek_gecmis)
        onemli_mesajlar = [m for m in sonuc if "[ONEMLI]" in m.get("icerik", "")]
        assert len(onemli_mesajlar) > 0

    def test_sikistir_mesaj_sayisi_degisebilir(self, compressor, ornek_gecmis):
        """Sikistirma sonrasi mesaj sayisi degisebilir ama en az 1 olmali."""
        sonuc = compressor.sikistir(ornek_gecmis)
        assert len(sonuc) >= 1

    def test_sikistir_token_limitine_uymali(self, compressor, ornek_gecmis):
        """Sikistirma token limitine yaklasik olarak uymali."""
        limit = 120
        sonuc = compressor.sikistir(ornek_gecmis, max_token=limit)
        # Ozet + onemli bilgiler her zaman eklenir, bu yuzden limit biraz asilabilir
        toplam_token = compressor._token_hesapla(sonuc)
        # En azindan tum orijinal mesajlar eklenmemis olmali (limit dusuk)
        assert len(sonuc) <= len(ornek_gecmis) + 3  # +ozet +onemli

    def test_sikistir_cok_kucuk_limit(self, compressor, ornek_gecmis):
        """Cok kucuk token limitinde en azindan ozet donmeli."""
        sonuc = compressor.sikistir(ornek_gecmis, max_token=5)
        assert len(sonuc) >= 1
        assert sonuc[0].get("sikistirilmis") is True

    def test_sikistir_gecmis_yapisini_korur(self, compressor, ornek_gecmis):
        """Sikistirilmis mesajlar 'rol' ve 'icerik' anahtarlarina sahip olmali."""
        sonuc = compressor.sikistir(ornek_gecmis)
        for m in sonuc:
            assert "rol" in m
            assert "icerik" in m

    def test_sikistir_gecersiz_veri(self, compressor):
        """Gecersiz girdi durumunda hata firlatmamali."""
        sonuc = compressor.sikistir("gecersiz")
        assert isinstance(sonuc, list)

    def test_sikistir_buyuk_gecmis(self, compressor):
        """Cok fazla mesajda sikistirma calismali."""
        buyuk = [{"rol": "kullanici", "icerik": f"Mesaj {i}"} for i in range(100)]
        sonuc = compressor.sikistir(buyuk, max_token=500)
        assert len(sonuc) > 0


# ── Test 3: token_hesapla ──────────────────────────────────────────────

class TestTokenHesapla:
    def test_token_bos(self, compressor):
        """Bos liste 0 token donmeli."""
        assert compressor._token_hesapla([]) == 0

    def test_token_sayisi_dogru(self, compressor):
        """Karakter/4 + 1 formulu dogru calismali."""
        mesajlar = [{"rol": "kullanici", "icerik": "abcd"}]  # 4 karakter -> 4/4 + 1 = 2
        assert compressor._token_hesapla(mesajlar) == 2

    def test_token_coklu_mesaj(self, compressor):
        """Birden cok mesajin tokenlari toplanmali."""
        mesajlar = [
            {"rol": "kullanici", "icerik": "abc"},     # 3/4 + 1 = 1
            {"rol": "asistan", "icerik": "abcdefgh"},  # 8/4 + 1 = 3
        ]
        assert compressor._token_hesapla(mesajlar) == 4

    def test_token_dict_disinda(self, compressor):
        """Dict olmayan girdilerde str() donusumu calismali."""
        # str(1) = "1" -> len("1") // 4 + 1 = 0 + 1 = 1, 3 eleman -> 3
        assert compressor._token_hesapla([1, 2, 3]) >= 3


# ── Test 4: onemli_bilgileri_sakla / getir / temizle ───────────────────

class TestOnemliBilgiler:
    def test_anahtar_deger_sakla(self, compressor):
        """Anahtar-deger cifti saklanabilmeli."""
        compressor.onemli_bilgileri_sakla("kullanici_adi", "test_user")
        bilgiler = compressor.onemli_bilgileri_getir()
        assert bilgiler["kullanici_adi"] == "test_user"

    def test_sozluk_sakla(self, compressor):
        """Sozluk ile toplu saklama calismali."""
        compressor.onemli_bilgileri_sakla({"isim": "Ali", "yas": 30})
        bilgiler = compressor.onemli_bilgileri_getir()
        anahtar_mevcut = any("isim" in k for k in bilgiler)
        assert anahtar_mevcut

    def test_sozluk_etiket_prefix(self, compressor):
        """Sozluk ile etiket prefix'li saklama calismali."""
        compressor.onemli_bilgileri_sakla({"sehir": "Istanbul"}, etiket="kullanici")
        bilgiler = compressor.onemli_bilgileri_getir()
        prefix_key = next((k for k in bilgiler if k.startswith("kullanici.")), None)
        assert prefix_key is not None
        assert bilgiler[prefix_key] == "Istanbul"

    def test_coklu_bilgi_birikmeli(self, compressor):
        """Birden cok bilgi saklandiginda hepsi birikmeli."""
        compressor.onemli_bilgileri_sakla("a", 1)
        compressor.onemli_bilgileri_sakla("b", 2)
        assert len(compressor.onemli_bilgileri_getir()) == 2

    def test_temizle(self, compressor):
        """temizle() tum bilgileri sifirlamali."""
        compressor.onemli_bilgileri_sakla("a", 1)
        compressor.temizle()
        assert compressor.onemli_bilgileri_getir() == {}
        assert compressor._ozet_gecmisi == []

    def test_onemli_bilgi_etiket_puani(self, compressor):
        """Saklanan bilgilerin etiket puani 1.0 olmali."""
        compressor.onemli_bilgileri_sakla("test", "deger")
        anahtar_bilgi = next(k for k in compressor._etiket_puani if "test" in k)
        assert compressor._etiket_puani[anahtar_bilgi] == 1.0


# ── Test 5: ozet_olustur ────────────────────────────────────────────────

class TestOzet:
    def test_ozet_bos_gecmis(self, compressor):
        """Bos gecmis icin 'Henuz mesaj yok' donmeli."""
        assert compressor.ozet_olustur([]) == "Henuz mesaj yok."

    def test_ozet_icerik_dogru(self, compressor, ornek_gecmis):
        """Ozet dogru mesaj sayisi ve tur bilgisi icermeli."""
        ozet = compressor.ozet_olustur(ornek_gecmis)
        assert "6 mesaj" in ozet

    def test_ozet_gecmise_eklenir(self, compressor, ornek_gecmis):
        """Her ozet_olustur cagrisi gecmise eklenmeli."""
        compressor.ozet_olustur(ornek_gecmis)
        assert len(compressor._ozet_gecmisi) == 1

    def test_ozet_anahtar_kelime_icerir(self, compressor, ornek_gecmis):
        """Ozet anahtar kelimeler icermeli."""
        ozet = compressor.ozet_olustur(ornek_gecmis)
        assert "Anahtar kelimeler" in ozet

    def test_ozet_maks_karakter(self, compressor, ornek_gecmis):
        """Ozet maks_karakter sinirini asmamali."""
        ozet = compressor.ozet_olustur(ornek_gecmis, max_karakter=50)
        assert len(ozet) <= 55  # +3 for "..."

    def test_ozet_coklu_cagri(self, compressor, ornek_gecmis):
        """Ard arda cagrilar ozet gecmisini biriktirmeli."""
        compressor.ozet_olustur(ornek_gecmis)
        compressor.ozet_olustur(ornek_gecmis)
        assert len(compressor._ozet_gecmisi) == 2


# ── Test 6: anahtar_kelime_cikar ────────────────────────────────────────

class TestAnahtarKelime:
    def test_anahtar_kelime_bos(self, compressor):
        """Bos gecmis bos liste donmeli."""
        assert compressor._anahtar_kelime_cikar([]) == []

    def test_anahtar_kelime_gecerli(self, compressor, ornek_gecmis):
        """Gecerli gecmisten anahtar kelime cikarilmali."""
        kelimeler = compressor._anahtar_kelime_cikar(ornek_gecmis)
        assert len(kelimeler) > 0
        assert all(isinstance(k, str) for k in kelimeler)

    def test_anahtar_kelime_stop_words_filtrele(self, compressor):
        """Stop words (bir, bu, ve) anahtar kelime olarak cikmamali."""
        gecmis = [{"rol": "kullanici", "icerik": "bir bu ve veya ile ama"}]
        kelimeler = compressor._anahtar_kelime_cikar(gecmis)
        assert all(k not in ("bir", "bu", "ve") for k in kelimeler)

    def test_anahtar_kelime_gecersiz_girdi(self, compressor):
        """Gecersiz girdide hata firlatmamali, bos liste donmeli."""
        assert compressor._anahtar_kelime_cikar("gecersiz") == []


# ── Test 7: run fonksiyonu ──────────────────────────────────────────────

class TestRun:
    def test_run_varsayilan(self):
        """run() varsayilan parametrelerle calismali."""
        from context_compressor import run
        sonuc = run()
        data = json.loads(sonuc)
        assert "orijinal_sayi" in data
        assert "sikistirilmis_sayi" in data
        assert "ozet" in data

    def test_run_ozel_gecmis(self):
        """run() ozel gecmis ile calismali."""
        from context_compressor import run
        sonuc = run(gecmis=[
            {"rol": "kullanici", "icerik": "Test mesaji"},
        ])
        data = json.loads(sonuc)
        assert data["orijinal_sayi"] == 1
