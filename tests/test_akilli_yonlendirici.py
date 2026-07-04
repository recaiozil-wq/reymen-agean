# -*- coding: utf-8 -*-
"""akilli_yonlendirici.py testleri."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import akilli_yonlendirici as router


class TestGoreviSiniflandir:
    """gorevi_siniflandir() kategorizasyon testleri."""

    def test_hizli_kategori(self):
        assert router.gorevi_siniflandir("kisa bir ozet yap") == "hizli"
        assert router.gorevi_siniflandir("bu dosya var mi kontrol et") == "hizli"
        assert router.gorevi_siniflandir("bunu siniflandir") == "hizli"
        assert router.gorevi_siniflandir("hizli kontrol yap") == "hizli"
        assert router.gorevi_siniflandir("dogru mu kontrol et") == "hizli"

    def test_kod_kategori(self):
        assert router.gorevi_siniflandir("python kodu yaz") == "kod"
        assert router.gorevi_siniflandir("syntax hatasini duzelt") == "kod"
        assert router.gorevi_siniflandir("bu api'yi cagir") == "kod"
        assert router.gorevi_siniflandir("test yaz bu modul icin") == "kod"
        assert router.gorevi_siniflandir("fonksiyon debug et") == "kod"
        assert router.gorevi_siniflandir("import hatasini coz") == "kod"

    def test_mantik_kategori(self):
        assert router.gorevi_siniflandir("matematik problemini coz") == "mantik"
        assert router.gorevi_siniflandir("strateji olustur") == "mantik"
        assert router.gorevi_siniflandir("karsilastir ve en iyisini sec") == "mantik"
        assert router.gorevi_siniflandir("derinlemesine analiz yap") == "mantik"
        assert router.gorevi_siniflandir("karar ver hangisi daha iyi") == "mantik"

    def test_yaratici_kategori(self):
        assert router.gorevi_siniflandir("hikaye yaz") == "yaratici"
        assert router.gorevi_siniflandir("slogan uret") == "yaratici"
        assert router.gorevi_siniflandir("blog icerigi yaz") == "yaratici"
        assert router.gorevi_siniflandir("yaratici fikir uret") == "yaratici"
        assert router.gorevi_siniflandir("senaryo yaz") == "yaratici"

    def test_guvensiz_kategori(self):
        # Bu kelimeler sifre/hukuki/medikal ile eslesmeli
        assert router.gorevi_siniflandir("gizli veri isle") == "guvensiz"
        assert router.gorevi_siniflandir("pii temizle") == "guvensiz"
        assert router.gorevi_siniflandir("hukuki metin analizi") == "guvensiz"
        assert router.gorevi_siniflandir("medikal veri isle") == "guvensiz"
        assert router.gorevi_siniflandir("finans verisi") == "guvensiz"

    def test_genel_kategori(self):
        assert router.gorevi_siniflandir("merhaba dunya") == "genel"
        assert router.gorevi_siniflandir("nasilsin") == "genel"
        assert router.gorevi_siniflandir("") == "genel"
        assert router.gorevi_siniflandir("bugun hava nasil") == "genel"

    def test_guvensiz_onceceligi(self):
        """guvensiz kategori digerlerinden once gelmeli."""
        assert router.gorevi_siniflandir("gizli kod yaz") == "guvensiz"  # gizli > kod
        assert (
            router.gorevi_siniflandir("gizli matematik formulu") == "guvensiz"
        )  # gizli > mantik

    def test_kod_onceceligi(self):
        """kod, mantik/hizli/yaratici'dan once gelmeli."""
        assert router.gorevi_siniflandir("kod yaz ve karsilastir") == "kod"
        assert router.gorevi_siniflandir("python API test") == "kod"

    def test_turkce_karakterler(self):
        """Turkce karakterli kelimeler dogru kategorize edilmeli."""
        assert router.gorevi_siniflandir("gizli veri oluştur") == "guvensiz"
        assert router.gorevi_siniflandir("derinlemesine analiz yap") == "mantik"
        assert router.gorevi_siniflandir("kisa ozet cikar") == "hizli"


class TestGorevIcinModelSec:
    """gorev_icin_model_sec() secim mantigi testleri."""

    def test_bos_provider_listesi(self):
        """Provider yoksa varsayilan lmstudio donmeli."""
        prov, model = router.gorev_icin_model_sec("test", [])
        assert prov == "lmstudio"
        assert model == "varsayilan"

    def test_kod_icin_deepseek_oncelik(self):
        """Kod kategorisinde deepseek ilk tercih."""
        prov, model = router.gorev_icin_model_sec(
            "python kodu yaz", ["lmstudio", "deepseek", "groq"]
        )
        assert prov == "deepseek"

    def test_kod_icin_deepseek_yoksa_fallback(self):
        """Kod kategorisinde deepseek yoksa openai'ye dusmeli."""
        prov, _ = router.gorev_icin_model_sec(
            "python kodu yaz", ["lmstudio", "openai", "groq"]
        )
        assert prov == "openai"

    def test_hizli_icin_groq_oncelik(self):
        """Hizli kategorisinde groq ilk tercih."""
        prov, _ = router.gorev_icin_model_sec(
            "kisa kontrol et", ["lmstudio", "groq", "deepseek"]
        )
        assert prov == "groq"

    def test_mantik_icin_deepseek(self):
        """Mantik kategorisinde deepseek ilk tercih."""
        prov, _ = router.gorev_icin_model_sec(
            "karmasik matematik sorusu", ["lmstudio", "deepseek", "anthropic"]
        )
        assert prov == "deepseek"

    def test_guvensiz_icin_anthropic(self):
        """Guvenlik kritik kategorisinde anthropic ilk tercih."""
        prov, _ = router.gorev_icin_model_sec(
            "hukuki metni analiz et", ["lmstudio", "anthropic", "openai"]
        )
        assert prov == "anthropic"

    def test_yaratici_icin_anthropic(self):
        """Yaratici kategorisinde anthropic ilk tercih."""
        prov, _ = router.gorev_icin_model_sec(
            "hikaye yaz", ["lmstudio", "anthropic", "groq"]
        )
        assert prov == "anthropic"

    def test_genel_icin_lmstudio(self):
        """Genel kategoride lmstudio ilk tercih."""
        prov, _ = router.gorev_icin_model_sec(
            "merhaba", ["lmstudio", "groq", "deepseek"]
        )
        assert prov == "lmstudio"

    def test_kuvvetli_mod_yukseltir(self):
        """Kuvvetli modda genel/hizli mantik tercihlerine yukseltilmeli."""
        prov, _ = router.gorev_icin_model_sec(
            "kisa ozet", ["lmstudio", "deepseek"], kuvvetli_mod=True
        )
        assert prov == "deepseek"  # mantik tercihi

    def test_model_adi_dogru(self):
        """Provider'a gore dogru model adi donmeli."""
        _, model = router.gorev_icin_model_sec("python kodu yaz", ["deepseek"])
        assert model == "deepseek-reasoner"

        _, model = router.gorev_icin_model_sec("kisa ozet", ["groq"])
        assert model == "llama-3.1-8b-instant"

    def test_musait_olmayan_provider_atlanir(self):
        """Musait olmayan provider listede yoksa atlanir."""
        prov, _ = router.gorev_icin_model_sec("kod yaz", ["sanal_provider"])
        assert prov == "sanal_provider"  # ilk musait

    def test_kuvvetli_mod_hizliyi_yukseltir(self):
        """kuvvetli_mod=True'da hizli kategorisi mantik tercihlerini kullanir."""
        prov, model = router.gorev_icin_model_sec(
            "kisa ozet", ["lmstudio", "deepseek", "anthropic"], kuvvetli_mod=True
        )
        assert prov == "deepseek"
        assert model == "deepseek-reasoner"


class TestStratejikAjanSec:
    """stratejik_ajan_sec() hata tabanli ajan degistirme testleri."""

    def test_hata_yoksa_mevcut_kalir(self):
        assert router.stratejik_ajan_sec("genel_cozucu", None) == "genel_cozucu"

    def test_syntax_hata_kod_uzmani(self):
        assert (
            router.stratejik_ajan_sec("genel_cozucu", "SyntaxError: invalid syntax")
            == "kod_uzmani"
        )

    def test_import_hata_kod_uzmani(self):
        assert (
            router.stratejik_ajan_sec("genel_cozucu", "ImportError: no module named x")
            == "kod_uzmani"
        )

    def test_timeout_sistem_mimari(self):
        assert (
            router.stratejik_ajan_sec(
                "genel_cozucu", "TimeoutError: connection timed out"
            )
            == "sistem_mimari"
        )

    def test_dosya_bulunamadi_sistem_mimari(self):
        assert (
            router.stratejik_ajan_sec("genel_cozucu", "FileNotFoundError: no such file")
            == "sistem_mimari"
        )

    def test_permission_error_sistem_mimari(self):
        """PermissionError sistem_mimari'ye gitmeli (kod hata onceligi degil)."""
        assert (
            router.stratejik_ajan_sec("genel_cozucu", "PermissionError: access denied")
            == "sistem_mimari"
        )

    def test_rate_limit_guvenlik_uzmani(self):
        assert (
            router.stratejik_ajan_sec("genel_cozucu", "rate limit asildi")
            == "guvenlik_uzmani"
        )

    def test_veritabani_veri_uzmani(self):
        assert (
            router.stratejik_ajan_sec(
                "genel_cozucu", "sqlite3.OperationalError: no such table"
            )
            == "veri_uzmani"
        )

    def test_json_decode_veri_uzmani(self):
        assert (
            router.stratejik_ajan_sec("genel_cozucu", "json.decoder.JSONDecodeError")
            == "veri_uzmani"
        )

    def test_utf8_veri_uzmani(self):
        assert (
            router.stratejik_ajan_sec("genel_cozucu", "UnicodeDecodeError: utf-8")
            == "veri_uzmani"
        )

    def test_tanimsiz_hata_mevcut_kalir(self):
        assert (
            router.stratejik_ajan_sec("veri_uzmani", "bilinmeyen hata") == "veri_uzmani"
        )

    def test_kod_onceceligi_guvenlige_gore(self):
        """Kod hatalari guvenlik hatalarindan once kontrol edilmeli."""
        # SyntaxError icinde 'forbidden' kelimesi gecse bile kod_uzmani secilmeli
        sonuc = router.stratejik_ajan_sec(
            "genel_cozucu", "SyntaxError: forbidden token"
        )
        assert sonuc == "kod_uzmani"

    def test_buyuk_kucuk_duyarsiz(self):
        """Hata mesaji buyuk/kucuk harf duyarsiz kontrol edilmeli."""
        assert router.stratejik_ajan_sec("genel_cozucu", "SYNTAXERROR") == "kod_uzmani"
        assert router.stratejik_ajan_sec("genel_cozucu", "TIMEOUT") == "sistem_mimari"

    def test_bos_hata_mesaji(self):
        assert router.stratejik_ajan_sec("kod_uzmani", "") == "kod_uzmani"


class TestAjanTalimatiniGetir:
    def test_gecerli_ajan(self):
        talimat = router.ajan_talimatini_getir("kod_uzmani")
        assert "Python" in talimat
        assert len(talimat) > 50

    def test_gecersiz_ajan_genel_cozucu_fallback(self):
        talimat = router.ajan_talimatini_getir("olmayan_ajan")
        assert "mantik" in talimat or "analitik" in talimat

    def test_tum_personalarin_talimati_var(self):
        for ajan_id in router.AJAN_PERSONALARI:
            talimat = router.ajan_talimatini_getir(ajan_id)
            assert len(talimat) > 30

    def test_guvenlik_uzmani_talimati(self):
        talimat = router.ajan_talimatini_getir("guvenlik_uzmani")
        assert "siber" in talimat or "guvenlik" in talimat


class TestYonlendirmeAcikla:
    def test_format(self):
        sonuc = router.yonlendirme_acikla("kod yaz", ["lmstudio", "deepseek"])
        assert "[Router]" in sonuc
        assert "Kategori:" in sonuc
        assert "Secilen:" in sonuc
        assert "Musait:" in sonuc

    def test_dogru_kategori(self):
        sonuc = router.yonlendirme_acikla("Python kodu yaz", ["lmstudio", "deepseek"])
        assert "kod" in sonuc


class TestMusaitProviderlarBul:
    def test_bos_config(self):
        assert router.musait_providerlar_bul({}) == []

    def test_yerel_providerlar_her_zaman_musait(self):
        config = {"providers": {"lmstudio": {"api_key": "not-needed"}}}
        musait = router.musait_providerlar_bul(config)
        assert "lmstudio" in musait

    def test_api_key_ile(self):
        config = {"providers": {"deepseek": {"api_key": "sk-test-123"}}}
        # lmstudio her zaman eklenir
        musait = router.musait_providerlar_bul(config)
        # lmstudio her zaman var (yerel)
        assert "deepseek" in musait

    def test_masked_key_filtrele(self):
        config = {"providers": {"openai": {"api_key": "***"}}}
        musait = router.musait_providerlar_bul(config)
        assert "openai" not in musait

    def test_karisik(self):
        config = {
            "providers": {
                "lmstudio": {"api_key": "not-needed"},
                "deepseek": {"api_key": "sk-real-456"},
                "openai": {"api_key": "***"},
                "anthropic": {"api_key": ""},
            }
        }
        musait = router.musait_providerlar_bul(config)
        assert "lmstudio" in musait
        assert "deepseek" in musait
        assert "openai" not in musait
        assert "anthropic" not in musait


class TestVarsayilanModel:
    def test_tum_providerlar(self):
        for prov, beklenen in [
            ("deepseek", "deepseek-chat"),
            ("openai", "gpt-4o-mini"),
            ("anthropic", "claude-haiku-4-5-20251001"),
            ("groq", "llama-3.1-8b-instant"),
            ("ollama", "llama3.1:8b"),
            ("lmstudio", "varsayilan"),
            ("bilinmeyen", "varsayilan"),
        ]:
            assert router._varsayilan_model(prov) == beklenen
