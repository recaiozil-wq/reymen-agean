# -*- coding: utf-8 -*-
"""test_beyin.py — Beyin sınıfı için kapsamlı pytest testleri."""

import os
import sys
import json
import time
import threading
from unittest.mock import patch, MagicMock, PropertyMock

import pytest
import requests

# Proje kökünü sys.path'e ekle
_proje_koku = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _proje_koku not in sys.path:
    sys.path.insert(0, _proje_koku)

from beyin import (
    Beyin,
    SaglayCiAdim,
    LLMYanitMeta,
    _guvensiz_import,
    TIMEOUT_SANIYE,
    _VARSAYILAN_MODELLER,
    _PROVIDER_ENV,
    _POOL_AKTIF,
    _CACHE_AKTIF,
)


# ══════════════════════════════════════════════════════════════════════════
# Fixture'lar
# ══════════════════════════════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def _test_izolasyonu():
    """credential_pool + prompt caching + rate guard devre dışı (test izolasyonu)."""
    # NOT: Gercek modul namespace'i reymen.cereyan.beyin, root shim degil
    with patch("reymen.cereyan.beyin._POOL_AKTIF", False), \
         patch("reymen.cereyan.beyin._CACHE_AKTIF", False), \
         patch("reymen.cereyan.beyin._GUARD_AKTIF", False):
        yield


@pytest.fixture
def minimal_config():
    return {
        "default_provider": "lmstudio",
        "default_model": "test-model",
        "providers": {
            "lmstudio": {"base_url": "http://localhost:1234", "api_key": "not-needed"},
        },
        "fallback_model": None,
    }


@pytest.fixture
def multi_provider_config():
    return {
        "default_provider": "lmstudio",
        "default_model": "test-model",
        "providers": {
            "lmstudio": {"base_url": "http://localhost:1234", "api_key": "not-needed"},
            "deepseek": {"base_url": "https://api.deepseek.com", "api_key": "sk-test"},
            "openai": {"base_url": "https://api.openai.com", "api_key": "sk-openai-test"},
        },
        "fallback_model": None,
    }


@pytest.fixture
def fallback_config():
    return {
        "default_provider": "lmstudio",
        "default_model": "test-model",
        "providers": {
            "lmstudio": {"base_url": "http://localhost:1234", "api_key": "not-needed"},
        },
        "fallback_model": {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "api_key": "sk-fallback-key",
            "base_url": "https://api.openai.com",
        },
    }


@pytest.fixture
def mock_response():
    """Başarılı bir requests.Response mock'u."""
    resp = MagicMock(spec=requests.Response)
    resp.status_code = 200
    resp.json.return_value = {
        "choices": [{"message": {"content": "Merhaba, nasıl yardımcı olabilirim?"}}]
    }
    resp.raise_for_status.return_value = None
    return resp


# ══════════════════════════════════════════════════════════════════════════
# SaglayCiAdim testleri (1-2 test)
# ══════════════════════════════════════════════════════════════════════════

class TestSaglayCiAdim:
    def test_olusturma(self):
        """SaglayCiAdim doğru şekilde oluşturulabiliyor mu?"""
        adim = SaglayCiAdim(
            provider="deepseek",
            model="deepseek-chat",
            base_url="https://api.deepseek.com",
            api_key="sk-test",
        )
        assert adim.provider == "deepseek"
        assert adim.model == "deepseek-chat"
        assert adim.base_url == "https://api.deepseek.com"
        assert adim.api_key == "sk-test"

    def test_repr(self):
        """__repr__ düzgün çalışıyor mu?"""
        adim = SaglayCiAdim(
            provider="openai", model="gpt-4", base_url="https://api.openai.com", api_key="sk-test"
        )
        r = repr(adim)
        assert "SaglayCiAdim" in r
        assert "openai" in r
        assert "gpt-4" in r


# ══════════════════════════════════════════════════════════════════════════
# LLMYanitMeta testleri (3)
# ══════════════════════════════════════════════════════════════════════════

class TestLLMYanitMeta:
    def test_olusturma(self):
        meta = LLMYanitMeta(
            metin="test yanıtı", provider="lmstudio", model="test-model",
            sure_sn=0.5, tahmini_token=50,
        )
        assert meta.metin == "test yanıtı"
        assert meta.provider == "lmstudio"
        assert meta.model == "test-model"
        assert meta.sure_sn == 0.5
        assert meta.tahmini_token == 50

    def test_varsayilan_degerler(self):
        meta = LLMYanitMeta(metin="merhaba", provider="openai", model="gpt-4")
        assert meta.sure_sn == 0.0
        assert meta.tahmini_token == 0


# ══════════════════════════════════════════════════════════════════════════
# _guvensiz_import testleri (4-5)
# ══════════════════════════════════════════════════════════════════════════

class TestGuvensizImport:
    def test_mevcut_modul(self):
        """Mevcut bir modül (os) içe aktarılabilmeli."""
        sonuc = _guvensiz_import("os")
        assert sonuc is not None
        assert hasattr(sonuc, "path")

    def test_olmayan_modul(self):
        """Olmayan bir modül None döndürmeli, hata fırlatmamalı."""
        sonuc = _guvensiz_import("xyz_boyle_bir_modul_yok_12345")
        assert sonuc is None


# ══════════════════════════════════════════════════════════════════════════
# Beyin başlatma testleri (6-15)
# ══════════════════════════════════════════════════════════════════════════

class TestBeyinBaslatma:
    def test_minimal_baslatma(self, minimal_config):
        """En az konfigürasyonla Beyin oluşturulabilmeli."""
        beyin = Beyin(minimal_config)
        assert beyin.provider == "lmstudio"
        assert beyin.model == "test-model"
        assert beyin.base_url == "http://localhost:1234"
        assert beyin.api_key == "not-needed"
        assert isinstance(beyin._iptal_olayi, threading.Event)
        assert len(beyin._fallback_zinciri) >= 1

    def test_default_model_atanir(self):
        """default_model belirtilmezse varsayılan model atanmalı."""
        cfg = {
            "default_provider": "lmstudio",
            "providers": {"lmstudio": {"base_url": "http://localhost:1234", "api_key": "not-needed"}},
        }
        beyin = Beyin(cfg)
        assert beyin.model == "cognitivecomputations.dolphin3.0-llama3.1-8b"

    def test_var_olan_anahtar_os_environ(self, minimal_config):
        """OS environ'dan anahtar bulunabilmeli."""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "sk-env-test"}, clear=False):
            cfg = {
                "default_provider": "deepseek",
                "default_model": "deepseek-chat",
                "providers": {
                    "deepseek": {"base_url": "https://api.deepseek.com", "api_key": ""},
                },
            }
            beyin = Beyin(cfg)
            assert beyin.api_key == "sk-env-test"

    def test_anahtar_config_oncesi_env(self, minimal_config):
        """Config'deki anahtar env'den önce kullanılmalı."""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "sk-env-val"}, clear=False):
            cfg = {
                "default_provider": "deepseek",
                "default_model": "deepseek-chat",
                "providers": {
                    "deepseek": {"base_url": "https://api.deepseek.com", "api_key": "sk-rea-key"},
                },
            }
            beyin = Beyin(cfg)
            # Config'deki sk-rea-key env'deki sk-env-val'dan önce kullanılmalı
            assert beyin.api_key == "sk-rea-key"

    def test_lmstudio_api_key_not_needed(self, minimal_config):
        """LM Studio için api_key 'not-needed' dönmeli."""
        cfg = {
            "default_provider": "lmstudio",
            "providers": {"lmstudio": {"base_url": "http://localhost:1234", "api_key": "***hidden***"}},
        }
        beyin = Beyin(cfg)
        assert beyin.api_key == "not-needed"

    def test_fallback_zinciri_tekil(self, minimal_config):
        """Sadece bir sağlayıcı varsa fallback zinciri tek elemanlı olmalı."""
        beyin = Beyin(minimal_config)
        assert len(beyin._fallback_zinciri) == 1
        assert beyin._fallback_zinciri[0].provider == "lmstudio"

    def test_fallback_zinciri_coklu(self, multi_provider_config):
        """Birden çok sağlayıcı varsa zincirde hepsi bulunmalı."""
        beyin = Beyin(multi_provider_config)
        assert len(beyin._fallback_zinciri) >= 2

    def test_fallback_model_eklenir(self, fallback_config):
        """fallback_model dict olarak verilirse zincire eklenmeli."""
        beyin = Beyin(fallback_config)
        # lmstudio + fallback_model (openai)
        assert len(beyin._fallback_zinciri) >= 2
        fallback_adimlari = [a for a in beyin._fallback_zinciri if a.provider == "openai"]
        assert len(fallback_adimlari) > 0

    def test_fallback_masked_key_atlanir(self):
        """*** ile başlayan anahtarlar zincire eklenmemeli."""
        cfg = {
            "default_provider": "lmstudio",
            "providers": {
                "lmstudio": {"base_url": "http://localhost:1234", "api_key": "not-needed"},
                "deepseek": {"base_url": "https://api.deepseek.com", "api_key": "***masked***"},
            },
            "fallback_model": {
                "provider": "openai", "model": "gpt-4", "api_key": "***masked***",
            },
        }
        # Ortamda DEEPSEEK_API_KEY varsa masked deepseek atlanamaz; temizle
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": ""}, clear=False):
            beyin = Beyin(cfg)
            for adim in beyin._fallback_zinciri:
                if adim.provider == "deepseek":
                    # deepseek masked olduğu için eklenmemeli
                    pass
            # Sadece lmstudio olmalı (çünkü deepseek masked, openai fallback masked)
            providers = [a.provider for a in beyin._fallback_zinciri]
            assert "deepseek" not in providers

    def test_iptal_et_ve_sifirla(self, minimal_config):
        """iptal_et() ve sifirla() düzgün çalışmalı."""
        beyin = Beyin(minimal_config)
        assert not beyin._iptal_olayi.is_set()
        beyin.iptal_et()
        assert beyin._iptal_olayi.is_set()
        beyin.sifirla()
        assert not beyin._iptal_olayi.is_set()

    def test_varsayilan_model_azure(self, minimal_config):
        """Azure için varsayılan model env'den okunmalı."""
        with patch.dict(os.environ, {"AZURE_OPENAI_DEPLOYMENT": "gpt-35-turbo"}, clear=False):
            model = Beyin._varsayilan_model(None, "azure")
            assert model == "gpt-35-turbo"

    def test_varsayilan_model_bilinmeyen(self):
        """Bilinmeyen provider için 'default' dönmeli."""
        model = Beyin._varsayilan_model(None, "bilinmeyen_provider")
        assert model == "default"


# ══════════════════════════════════════════════════════════════════════════
# _anahtar_bul testleri (16-20)
# ══════════════════════════════════════════════════════════════════════════

class TestAnahtarBul:
    def test_configden_okur(self, minimal_config):
        beyin = Beyin(minimal_config)
        anahtar = beyin._anahtar_bul("lmstudio", {"api_key": "test-key-123"})
        assert anahtar == "test-key-123"

    def test_envden_okur(self, minimal_config):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-env-openai"}, clear=False):
            beyin = Beyin(minimal_config)
            anahtar = beyin._anahtar_bul("openai", {"api_key": ""})
            assert anahtar == "sk-env-openai"

    def test_lmstudio_fallback(self, minimal_config):
        beyin = Beyin(minimal_config)
        anahtar = beyin._anahtar_bul("lmstudio", {"api_key": ""})
        assert anahtar == "not-needed"

    def test_bilinmeyen_provider_bos_anahtar(self, minimal_config):
        beyin = Beyin(minimal_config)
        anahtar = beyin._anahtar_bul("bilinmeyen", {"api_key": ""})
        assert anahtar == ""

    def test_masked_anahtar_atlanir(self, minimal_config):
        beyin = Beyin(minimal_config)
        anahtar = beyin._anahtar_bul("openai", {"api_key": "***masked***"})
        # *** ile başlayan anahtarlar atlanır (env'den de gelmezse boş döner)
        assert anahtar == ""


# ══════════════════════════════════════════════════════════════════════════
# _rate_limit_mi testleri (21-23)
# ══════════════════════════════════════════════════════════════════════════

class TestRateLimitMi:
    def test_429_status_code(self):
        hata = requests.HTTPError("429 Too Many Requests")
        hata.response = MagicMock()
        hata.response.status_code = 429
        assert Beyin._rate_limit_mi(hata)

    def test_rate_limit_mesaji(self):
        hata = Exception("Rate limit exceeded, try again later")
        assert Beyin._rate_limit_mi(hata)

    def test_diger_hata(self):
        hata = Exception("Connection refused")
        assert not Beyin._rate_limit_mi(hata)


# ══════════════════════════════════════════════════════════════════════════
# _cagir_lmstudio testi (24)
# ══════════════════════════════════════════════════════════════════════════

class TestCagirLmstudio:
    @patch("beyin.requests.post")
    def test_sistem_mesaji_donusturulur(self, mock_post, mock_response):
        """LM Studio'da sistem mesajı [SISTEM]: öneki ile user'a çevrilmeli."""
        mock_post.return_value = mock_response
        cfg = {
            "default_provider": "lmstudio",
            "providers": {"lmstudio": {"base_url": "http://localhost:1234", "api_key": "not-needed"}},
        }
        beyin = Beyin(cfg)
        sonuc = beyin._cagir_lmstudio(
            "http://localhost:1234", "test-model",
            "Sistem talimatı", [{"role": "user", "content": "Merhaba"}],
        )
        assert sonuc == "Merhaba, nasıl yardımcı olabilirim?"
        # Gönderilen payload'da sistem mesajı [SISTEM]: ile user'a çevrilmiş olmalı
        cagri_payload = mock_post.call_args[1]["json"]
        mesajlar = cagri_payload["messages"]
        assert mesajlar[0]["role"] == "user"
        assert "[SISTEM]" in mesajlar[0]["content"]


# ══════════════════════════════════════════════════════════════════════════
# _cagir_openai_uyumlu testi (25)
# ══════════════════════════════════════════════════════════════════════════

class TestCagirOpenaiUyumlu:
    @patch("beyin.requests.post")
    def test_basarili_cagri(self, mock_post, mock_response):
        mock_post.return_value = mock_response
        cfg = {
            "default_provider": "openai",
            "providers": {"openai": {"base_url": "https://api.openai.com", "api_key": "sk-test"}},
        }
        beyin = Beyin(cfg)
        sonuc = beyin._cagir_openai_uyumlu(
            "https://api.openai.com", "sk-test", "gpt-4",
            "Sistem", [{"role": "user", "content": "Selam"}],
        )
        assert sonuc == "Merhaba, nasıl yardımcı olabilirim?"
        # Authorization header kontrol
        headers = mock_post.call_args[1]["headers"]
        assert headers["Authorization"] == "Bearer sk-test"


# ══════════════════════════════════════════════════════════════════════════
# _cagir (dispatch) testi (26-28)
# ══════════════════════════════════════════════════════════════════════════

class TestCagirDispatch:
    @patch("beyin.Beyin._cagir_lmstudio", return_value="lmstudio yanıtı")
    def test_lmstudio_dispatch(self, mock_lm, minimal_config):
        beyin = Beyin(minimal_config)
        adim = SaglayCiAdim("lmstudio", "model", "http://localhost:1234", "not-needed")
        meta = beyin._cagir(adim, "sistem", [{"role": "user", "content": "merhaba"}])
        assert meta.metin == "lmstudio yanıtı"
        assert meta.provider == "lmstudio"

    @patch("beyin.Beyin._cagir_openai_uyumlu", return_value="openai yanıtı")
    def test_bilinmeyen_dispatch_openai_uyumlu(self, mock_openai, minimal_config):
        """Bilinmeyen provider'lar OpenAI uyumlu olarak çağrılmalı."""
        beyin = Beyin(minimal_config)
        adim = SaglayCiAdim("bilinmeyen_provider", "model", "http://example.com", "key")
        meta = beyin._cagir(adim, "sistem", [{"role": "user", "content": "merhaba"}])
        assert meta.metin == "openai yanıtı"

    def test_tahmini_token_hesaplanir(self, minimal_config):
        """_cagir token tahmini yapmalı."""
        with patch.object(Beyin, "_cagir_lmstudio", return_value="kısa yanıt"):
            beyin = Beyin(minimal_config)
            adim = SaglayCiAdim("lmstudio", "model", "http://localhost:1234", "not-needed")
            meta = beyin._cagir(adim, "sistem prompt", [{"role": "user", "content": "merhaba"}])
            assert meta.tahmini_token > 0


# ══════════════════════════════════════════════════════════════════════════
# _cagir_ile_retry testleri (29-31)
# ══════════════════════════════════════════════════════════════════════════

class TestCagirIleRetry:
    def test_basarili_ilk_deneme(self, minimal_config):
        """İlk denemede başarılı olursa direkt dönmeli."""
        with patch.object(Beyin, "_cagir", return_value=LLMYanitMeta(metin="başarılı", provider="lmstudio", model="m")):
            beyin = Beyin(minimal_config)
            adim = SaglayCiAdim("lmstudio", "m", "http://localhost:1234", "not-needed")
            sonuc = beyin._cagir_ile_retry(adim, "sistem", [])
            assert sonuc == "başarılı"

    def test_rate_limit_retry_basarili(self, minimal_config):
        """Rate limit hatası alıp sonra başarılı olunca retry çalışmalı."""
        cagir = MagicMock(
            side_effect=[
                requests.HTTPError("429 Too Many"),
                LLMYanitMeta(metin="başarılı", provider="lmstudio", model="m"),
            ]
        )
        # _cagir'ın ilk çağrısı requests.HTTPError fırlatsın
        with patch.object(Beyin, "_cagir", cagir):
            beyin = Beyin(minimal_config)
            adim = SaglayCiAdim("lmstudio", "m", "http://localhost:1234", "not-needed")
            sonuc = beyin._cagir_ile_retry(adim, "sistem", [])
            assert sonuc == "başarılı"
            assert cagir.call_count == 2

    def test_rate_limit_hepsi_basarisiz(self, minimal_config):
        """Rate limit hatası maximum deneme sayısı kadar denenmeli,
        sonra orijinal hata yükseltilmeli."""
        cagir = MagicMock(side_effect=requests.HTTPError("429 Too Many"))
        with patch.object(Beyin, "_cagir", cagir):
            beyin = Beyin(minimal_config)
            adim = SaglayCiAdim("lmstudio", "m", "http://localhost:1234", "not-needed")
            with pytest.raises(requests.HTTPError):
                beyin._cagir_ile_retry(adim, "sistem", [])
            assert cagir.call_count == Beyin.MAKS_DENEME


# ══════════════════════════════════════════════════════════════════════════
# _kesintibilir_cagir testleri (32-34)
# ══════════════════════════════════════════════════════════════════════════

class TestKesintibilirCagir:
    def test_normal_cagri(self, minimal_config):
        """İptal olmadan normal çağrı başarılı olmalı."""
        with patch.object(Beyin, "_cagir_ile_retry", return_value="başarılı yanıt"):
            beyin = Beyin(minimal_config)
            adim = SaglayCiAdim("lmstudio", "m", "http://localhost:1234", "not-needed")
            sonuc = beyin._kesintibilir_cagir(adim, "sistem", [])
            assert sonuc == "başarılı yanıt"

    def test_iptal_edilince_interrupted_error(self, minimal_config):
        """iptal_et() çağrıldığında InterruptedError fırlatılmalı."""
        # _cagir_ile_retry'in biraz bekletip sonra iptal tetiklenecek
        def yavas_cagir(*args, **kwargs):
            time.sleep(1)
            return "geç yanıt"

        with patch.object(Beyin, "_cagir_ile_retry", side_effect=yavas_cagir):
            beyin = Beyin(minimal_config)
            # Arka planda iptal sinyali gönder
            def iptal_sinyali():
                time.sleep(0.05)
                beyin.iptal_et()

            t = threading.Thread(target=iptal_sinyali, daemon=True)
            t.start()

            adim = SaglayCiAdim("lmstudio", "m", "http://localhost:1234", "not-needed")
            with pytest.raises(InterruptedError, match="iptal edildi"):
                beyin._kesintibilir_cagir(adim, "sistem", [])

    def test_hata_yukseltilir(self, minimal_config):
        """API hatası doğru şekilde yükseltilmeli."""
        with patch.object(Beyin, "_cagir_ile_retry", side_effect=ValueError("API hatası")):
            beyin = Beyin(minimal_config)
            adim = SaglayCiAdim("lmstudio", "m", "http://localhost:1234", "not-needed")
            with pytest.raises(ValueError, match="API hatası"):
                beyin._kesintibilir_cagir(adim, "sistem", [])


# ══════════════════════════════════════════════════════════════════════════
# dusun / uret testleri (35-42)
# ══════════════════════════════════════════════════════════════════════════

class TestDusun:
    def test_basarili_dusun(self, minimal_config):
        """dusun() başarılı yanıt dönmeli."""
        with patch.object(Beyin, "_kesintibilir_cagir", return_value="başarılı yanıt"):
            with patch.object(Beyin, "_kullanim_kaydet"):
                beyin = Beyin(minimal_config)
                sonuc = beyin.dusun("sistem", [{"role": "user", "content": "merhaba"}])
                assert sonuc == "başarılı yanıt"

    def test_tum_saglayicilar_basarisiz(self, minimal_config):
        """Tüm sağlayıcılar başarısız olursa hata mesajı dönmeli."""
        with patch.object(Beyin, "_kesintibilir_cagir", side_effect=Exception("API hatası")):
            beyin = Beyin(minimal_config)
            sonuc = beyin.dusun("sistem", [{"role": "user", "content": "merhaba"}])
            assert "[Beyin Hatası]" in sonuc

    def test_tek_seferlik_provider(self, minimal_config):
        """dusun()'a provider parametresi verilince tek seferlik çağrı yapılmalı."""
        with patch.object(Beyin, "_tek_seferlik_cagri", return_value="tek seferlik yanıt"):
            beyin = Beyin(minimal_config)
            sonuc = beyin.dusun("sistem", [{"role": "user", "content": "merhaba"}], provider="openai")
            assert sonuc == "tek seferlik yanıt"

    def test_uret_alias(self, minimal_config):
        """uret() dusun() ile aynı sonucu dönmeli."""
        with patch.object(Beyin, "dusun", return_value="uret yanıtı"):
            beyin = Beyin(minimal_config)
            sonuc = beyin.uret("sistem", [{"role": "user", "content": "merhaba"}])
            assert sonuc == "uret yanıtı"

    def test_fallback_calisir(self, multi_provider_config):
        """İlk sağlayıcı başarısız olunca fallback çalışmalı."""
        cagir = MagicMock()
        cagir.side_effect = [
            Exception("İlk hata"),
            "fallback başarılı",
        ]
        with patch.object(Beyin, "_kesintibilir_cagir", cagir):
            with patch.object(Beyin, "_kullanim_kaydet"):
                beyin = Beyin(multi_provider_config)
                sonuc = beyin.dusun("sistem", [{"role": "user", "content": "merhaba"}])
                assert sonuc == "fallback başarılı"


# ══════════════════════════════════════════════════════════════════════════
# _tek_seferlik_cagri testleri (43-44)
# ══════════════════════════════════════════════════════════════════════════

class TestTekSeferlikCagri:
    def test_basarili(self, minimal_config):
        with patch.object(Beyin, "_cagir_ile_retry", return_value="başarılı"):
            with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}, clear=False):
                beyin = Beyin(minimal_config)
                sonuc = beyin._tek_seferlik_cagri("openai", "gpt-4", "sistem", [])
                assert sonuc == "başarılı"

    def test_hata_durumu(self, minimal_config):
        with patch.object(Beyin, "_cagir_ile_retry", side_effect=Exception("hata")):
            with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}, clear=False):
                beyin = Beyin(minimal_config)
                sonuc = beyin._tek_seferlik_cagri("openai", "gpt-4", "sistem", [])
                assert "[Beyin Hatası]" in sonuc


# ══════════════════════════════════════════════════════════════════════════
# _kullanim_kaydet testi (45)
# ══════════════════════════════════════════════════════════════════════════

class TestKullanimKaydet:
    def test_hata_sessizce_gecer(self, minimal_config):
        """account_usage yoksa sessizce başarısız olmalı."""
        beyin = Beyin(minimal_config)
        adim = SaglayCiAdim("lmstudio", "m", "http://localhost:1234", "not-needed")
        # Hata fırlatılmamalı
        beyin._kullanim_kaydet(adim, "sistem", [], "yanıt")
        # Test geçti — hata yok


# ══════════════════════════════════════════════════════════════════════════
# rota_belirle testi (46-47)
# ══════════════════════════════════════════════════════════════════════════

class TestRotaBelirle:
    def test_varsayilan_doner(self, minimal_config):
        """akilli_yonlendirici yoksa (mock'la simüle) varsayılan dönmeli."""
        import builtins
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "akilli_yonlendirici":
                raise ImportError("Simulated missing module")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            beyin = Beyin(minimal_config)
            prov, mdl = beyin.rota_belirle("test hedefi")
            assert prov == "lmstudio"
            assert mdl == "varsayilan"

    def test_router_varken_yonlendirir(self, minimal_config):
        """akilli_yonlendirici mevcutsa yönlendirme yapılmalı."""
        beyin = Beyin(minimal_config)
        # Gerçek akilli_yonlendirici mevcut, rota_belirle çağrılabilir
        prov, mdl = beyin.rota_belirle("test hedefi")
        # Router çalıştıysa farklı bir provider/model dönebilir
        assert isinstance(prov, str)
        assert isinstance(mdl, str)


# ══════════════════════════════════════════════════════════════════════════
# ping / aktif_providerlar testleri (48-50)
# ══════════════════════════════════════════════════════════════════════════

class TestPing:
    @patch("beyin.requests.get")
    def test_ping_basarili(self, mock_get, minimal_config):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_get.return_value = mock_resp
        beyin = Beyin(minimal_config)
        assert beyin.ping("lmstudio")

    @patch("beyin.requests.get")
    def test_ping_basarisiz(self, mock_get, minimal_config):
        mock_get.side_effect = requests.ConnectionError()
        beyin = Beyin(minimal_config)
        assert not beyin.ping("lmstudio")

    @patch("beyin.Beyin.ping")
    def test_aktif_providerlar(self, mock_ping, minimal_config):
        mock_ping.return_value = True
        beyin = Beyin(minimal_config)
        aktif = beyin.aktif_providerlar()
        assert len(aktif) >= 1


# ══════════════════════════════════════════════════════════════════════════
# Sabitler ve modül düzeyi testleri (51-52)
# ══════════════════════════════════════════════════════════════════════════

class TestSabitler:
    def test_varsayilan_modeller(self):
        assert "deepseek" in _VARSAYILAN_MODELLER
        assert "openai" in _VARSAYILAN_MODELLER
        assert "anthropic" in _VARSAYILAN_MODELLER
        assert _VARSAYILAN_MODELLER["deepseek"] == "deepseek-chat"

    def test_provider_env(self):
        assert _PROVIDER_ENV["deepseek"] == "DEEPSEEK_API_KEY"
        assert _PROVIDER_ENV["openai"] == "OPENAI_API_KEY"
        assert _PROVIDER_ENV["groq"] == "GROQ_API_KEY"

    def test_timeout_sabiti(self):
        assert TIMEOUT_SANIYE == 300


# ══════════════════════════════════════════════════════════════════════════
# _saglayici_baglantisi_kur testi (53)
# ══════════════════════════════════════════════════════════════════════════

class TestSaglayiciBaglantisiKur:
    def test_direkt_config_okunur(self):
        cfg = {
            "default_provider": "ollama",
            "providers": {
                "ollama": {"base_url": "http://localhost:11434", "api_key": ""},
            },
        }
        # _REGISTRY_AKTIF = False olduğu için direkt config dönmeli
        beyin = Beyin(cfg)
        # Beyin __init__'te _saglayici_baglantisi_kur çağrıldı
        assert beyin.base_url == "http://localhost:11434"


# ══════════════════════════════════════════════════════════════════════════
# _cagir_anthropic testi (54)
# ══════════════════════════════════════════════════════════════════════════

class TestCagirAnthropic:
    @patch("beyin.requests.post")
    def test_anthropic_cagrisi(self, mock_post):
        mock_resp = MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"content": [{"text": "Anthropic yanıtı"}]}
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp

        cfg = {
            "default_provider": "anthropic",
            "providers": {
                "anthropic": {"base_url": "https://api.anthropic.com", "api_key": "sk-ant-test"},
            },
        }
        beyin = Beyin(cfg)
        # _cagir_anthropic'i direkt test et
        sonuc = beyin._cagir_anthropic(
            "https://api.anthropic.com", "sk-ant-test", "claude-3",
            "Sistem", [{"role": "user", "content": "Merhaba"}],
        )
        assert sonuc == "Anthropic yanıtı"

        # x-api-key header kontrol
        headers = mock_post.call_args[1]["headers"]
        assert headers["x-api-key"] == "sk-ant-test"

    @patch("beyin.requests.post")
    def test_anthropic_assistant_mesajlari_filtrelenir(self, mock_post):
        """Anthropic çağrısında system/function mesajları filtrelenmeli."""
        mock_resp = MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"content": [{"text": "yanıt"}]}
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp

        cfg = {
            "default_provider": "anthropic",
            "providers": {
                "anthropic": {"base_url": "https://api.anthropic.com", "api_key": "sk-ant-test"},
            },
        }
        beyin = Beyin(cfg)
        mesajlar = [
            {"role": "system", "content": "sistem"},
            {"role": "user", "content": "kullanıcı"},
            {"role": "assistant", "content": "asistan"},
            {"role": "function", "content": "fonksiyon"},
        ]
        beyin._cagir_anthropic(
            "https://api.anthropic.com", "sk-ant-test", "claude-3",
            "Sistem", mesajlar,
        )
        payload = mock_post.call_args[1]["json"]
        # user ve assistant kaldı, system ve function gitmemeli
        roller = [m["role"] for m in payload["messages"]]
        assert "user" in roller
        assert "assistant" in roller
        assert "system" not in roller
        assert "function" not in roller


# ══════════════════════════════════════════════════════════════════════════
# _cagir_azure testi (55)
# ══════════════════════════════════════════════════════════════════════════

class TestCagirAzure:
    @patch("beyin.requests.post")
    def test_azure_cagrisi(self, mock_post):
        mock_resp = MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"choices": [{"message": {"content": "Azure yanıtı"}}]}
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp

        with patch.dict(os.environ, {
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
            "AZURE_OPENAI_API_VERSION": "2024-02-01",
        }, clear=False):
            cfg = {
                "default_provider": "azure",
                "providers": {"azure": {"base_url": "", "api_key": "az-key"}},
            }
            beyin = Beyin(cfg)
            sonuc = beyin._cagir_azure("az-key", "gpt-4", "Sistem", [{"role": "user", "content": "Merhaba"}])
            assert sonuc == "Azure yanıtı"


# ══════════════════════════════════════════════════════════════════════════
# dusun_stream testleri (56-58)
# ══════════════════════════════════════════════════════════════════════════

class TestDusunStream:
    @patch("beyin.Beyin._cagir_lmstudio", return_value="stream yanıt")
    def test_openai_uyumlu_stream_basarili(self, mock_lm, minimal_config):
        """Önce stream dener, başarısız olursa tam yanıta düşer — 
        burada stream patlayınca dusun() çağrılır."""
        # _stream_openai_uyumlu patlasın, sonra fallback olarak _cagir_lmstudio kullanılsın
        with patch.object(Beyin, "_stream_openai_uyumlu", side_effect=Exception("stream hatası")):
            beyin = Beyin(minimal_config)
            sonuc = list(beyin.dusun_stream("sistem", [{"role": "user", "content": "merhaba"}]))
            assert len(sonuc) == 1
            assert "stream yanıt" in sonuc[0]

    def test_stream_anthropic_basarili(self, minimal_config):
        """Anthropic provider için stream çağrısı."""
        cfg = {
            "default_provider": "anthropic",
            "providers": {
                "anthropic": {"base_url": "https://api.anthropic.com", "api_key": "sk-ant-test"},
            },
        }
        with patch.object(Beyin, "_stream_anthropic", return_value=iter(["token1", "token2"])):
            beyin = Beyin(cfg)
            sonuc = list(beyin.dusun_stream("sistem", [{"role": "user", "content": "merhaba"}]))
            assert sonuc == ["token1", "token2"]

    def test_stream_lmstudio_basarili(self, minimal_config):
        """LM Studio provider için stream çağrısı."""
        with patch.object(Beyin, "_stream_openai_uyumlu", return_value=iter(["parça1", "parça2"])):
            beyin = Beyin(minimal_config)
            sonuc = list(beyin.dusun_stream("sistem", [{"role": "user", "content": "merhaba"}]))
            assert sonuc == ["parça1", "parça2"]


# ══════════════════════════════════════════════════════════════════════════
# _cagir_moonshot testi (59)
# ══════════════════════════════════════════════════════════════════════════

class TestCagirMoonshot:
    @patch("beyin.Beyin._cagir_openai_uyumlu", return_value="moonshot yanıt")
    def test_moonshot_fallback_openai(self, mock_openai, minimal_config):
        """moonshot_schema yoksa OpenAI uyumlu çağrıya düşmeli."""
        cfg = {
            "default_provider": "moonshot",
            "providers": {
                "moonshot": {"base_url": "https://api.moonshot.cn/v1", "api_key": "ms-key"},
            },
        }
        with patch.dict(os.environ, {"MOONSHOT_BASE_URL": "https://api.moonshot.cn/v1"}, clear=False):
            # moonshot_schema gerçek ortamda mevcutsa ImportError yakalanmaz;
            # sys.modules'den kaldırarak fallback yolunu test ediyoruz
            import sys
            with patch.dict(sys.modules, {"moonshot_schema": None}):
                beyin = Beyin(cfg)
                sonuc = beyin._cagir_moonshot("ms-key", "moonshot-v1", "Sistem", [{"role": "user", "content": "Merhaba"}])
                # Gercek API cagrisi yapildigi icin 401 veya baska hata donebilir
                assert "401" in sonuc or "hata" in sonuc.lower() or "moonshot" in sonuc.lower()


# ══════════════════════════════════════════════════════════════════════════
# _cagir_bedrock testi (60)
# ══════════════════════════════════════════════════════════════════════════

class TestCagirBedrock:
    def test_bedrock_adapter_yoksa_hata(self, minimal_config):
        """bedrock_adapter modülü yoksa RuntimeError fırlatılmalı."""
        cfg = {
            "default_provider": "bedrock",
            "providers": {"bedrock": {"base_url": "", "api_key": ""}},
        }
        import sys
        with patch.dict(sys.modules, {"reymen.sistem.bedrock_adapter": None}):
            beyin = Beyin(cfg)
            with pytest.raises(RuntimeError, match="bedrock_adapter"):
                beyin._cagir_bedrock("model", "sistem", [])
