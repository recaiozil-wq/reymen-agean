"""test_beyin.py — Mock LLM testleri (API anahtari gerekmez).

Beyin.dusun() ve uret_v2() metodlarini unittest.mock ile test eder.
Gercek DeepSeek/OpenAI API'sine ihtiyac duymaz.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from reymen.cereyan.beyin import Beyin, SaglayCiAdim


# ── Test Fixture'lari ─────────────────────────────────────────────────────────

@pytest.fixture
def ornek_config():
    """Minimal ama gercekci Beyin config."""
    return {
        "default_provider": "deepseek",
        "default_model": "deepseek-v4-flash",
        "providers": {
            "deepseek": {
                "base_url": "https://api.deepseek.com",
                "api_key": "sk-test-key",
            },
            "openrouter": {
                "base_url": "https://openrouter.ai/api",
                "api_key": "sk-tes...uter",
            },
        },
    }


@pytest.fixture
def ornek_mesajlar():
    return [{"role": "user", "content": "Merhaba"}]


# ── Beyin Baslatma Testleri ──────────────────────────────────────────────────

class TestBeyinBaslatma:
    """Beyin(config) kurulumu."""

    def test_basit_baslatma(self, ornek_config):
        """Varsayilan provider/model dogru ataniyor mu?"""
        beyin = Beyin(config=ornek_config)
        assert beyin.provider == "deepseek"
        assert beyin.model == "deepseek-v4-flash"
        assert len(beyin._fallback_zinciri) >= 1

    def test_fallback_zinciri_olusuyor(self, ornek_config):
        """Fallback zincirinde provider'lar sirali mi?"""
        beyin = Beyin(config=ornek_config)
        zincir = beyin._fallback_zinciri
        assert isinstance(zincir, list)
        assert all(isinstance(adim, SaglayCiAdim) for adim in zincir)
        assert zincir[0].provider == "deepseek"

    def test_anahtar_bul_configten(self, ornek_config):
        """_anahtar_bul() config'deki key'i donduruyor mu?"""
        beyin = Beyin(config=ornek_config)
        anahtar = beyin._anahtar_bul("deepseek", {"api_key": "sk-test-key"})
        assert anahtar == "sk-test-key"

    def test_varsayilan_model_dondurur(self, ornek_config):
        """Bilinmeyen provider icin varsayilan model 'default' mu?"""
        beyin = Beyin(config=ornek_config)
        assert beyin._varsayilan_model("bilinmeyen") == "default"

    def test_iptal_mekanizmasi(self, ornek_config):
        """iptal_et() ve sifirla() calisiyor mu?"""
        beyin = Beyin(config=ornek_config)
        beyin.iptal_et()
        assert beyin._iptal_olayi.is_set()
        beyin.sifirla()
        assert not beyin._iptal_olayi.is_set()


# ── dusun() Basarili Cagri Testleri ──────────────────────────────────────────

class TestDusunBasarili:
    """Beyin.dusun() — normal akis (Mocked)."""

    def test_dusun_success(self, ornek_config, ornek_mesajlar):
        """En temel akis: sistem_prompt + mesaj -> yanit metni."""
        with patch.object(Beyin, "_cagir_openai_uyumlu",
                          return_value="Merhaba! Ben ReYMeN"):
            beyin = Beyin(config=ornek_config)
            yanit = beyin.dusun("Sen bir asistansin.", ornek_mesajlar)
            assert "ReYMeN" in yanit

    def test_dusun_uzun_yanit(self, ornek_config, ornek_mesajlar):
        """Uzun yanit metnini kesmeden donduruyor mu?"""
        uzun_metin = "Evet. " * 50
        with patch.object(Beyin, "_cagir_openai_uyumlu",
                          return_value=uzun_metin):
            beyin = Beyin(config=ornek_config)
            yanit = beyin.dusun("Sen bir asistansin.", ornek_mesajlar)
            assert len(yanit) > 100
            assert "Evet" in yanit

    def test_dusun_bos_yanit(self, ornek_config, ornek_mesajlar):
        """Provider bos content dondururse ne olur?"""
        with patch.object(Beyin, "_cagir_openai_uyumlu",
                          return_value=""):
            beyin = Beyin(config=ornek_config)
            yanit = beyin.dusun("Sen bir asistansin.", ornek_mesajlar)
            assert yanit is not None
            assert isinstance(yanit, str)


# ── Hata Senaryolari ─────────────────────────────────────────────────────────

class TestDusunHata:
    """Beyin.dusun() — hata durumlari."""

    def _yanit_beklenen_hata_iceriyor(self, yanit):
        """Yanit '[Beyin Hatasi]' veya '[Beyin Hatası]' iceriyor mu?"""
        return "[Beyin Hatası" in yanit or "[Beyin Hatasi" in yanit

    def test_tum_providerlar_basarisiz(self, ornek_config, ornek_mesajlar):
        """Tum provider'lar basarisiz -> hata mesaji."""
        with patch.object(Beyin, "_cagir_openai_uyumlu",
                          side_effect=RuntimeError("500 Internal Server Error")):
            beyin = Beyin(config=ornek_config)
            yanit = beyin.dusun("Sistem", ornek_mesajlar)
        assert self._yanit_beklenen_hata_iceriyor(yanit)

    def test_401_mesaji(self, ornek_config, ornek_mesajlar):
        """401 hatasinda uygun hata mesaji."""
        with patch.object(Beyin, "_cagir_openai_uyumlu",
                          side_effect=RuntimeError("401 Unauthorized")):
            beyin = Beyin(config=ornek_config)
            yanit = beyin.dusun("Sistem", ornek_mesajlar)
        assert self._yanit_beklenen_hata_iceriyor(yanit)

    def test_402_mesaji(self, ornek_config, ornek_mesajlar):
        """402 hatasinda kredi mesaji."""
        with patch.object(Beyin, "_cagir_openai_uyumlu",
                          side_effect=RuntimeError("402 Payment Required")):
            beyin = Beyin(config=ornek_config)
            yanit = beyin.dusun("Sistem", ornek_mesajlar)
        assert self._yanit_beklenen_hata_iceriyor(yanit)

    def test_429_mesaji(self, ornek_config, ornek_mesajlar):
        """429 hatasinda hiz siniri mesaji."""
        with patch.object(Beyin, "_cagir_openai_uyumlu",
                          side_effect=RuntimeError("429 Too Many Requests")):
            beyin = Beyin(config=ornek_config)
            yanit = beyin.dusun("Sistem", ornek_mesajlar)
        assert self._yanit_beklenen_hata_iceriyor(yanit)

    def test_fallback_openrouter_402(self, ornek_config, ornek_mesajlar):
        """DeepSeek 402 -> OpenRouter fallback calisiyor mu?"""
        cagrilan = []
        def mock_provider_call(*args, **kwargs):
            cagrilan.append(1)
            if len(cagrilan) == 1:
                raise RuntimeError("402 Payment Required")
            return "OpenRouter yaniti"

        with patch.object(Beyin, "_cagir_openai_uyumlu",
                          side_effect=mock_provider_call):
            beyin = Beyin(config=ornek_config)
            yanit = beyin.dusun("Sistem", ornek_mesajlar)
        assert yanit is not None
        assert "[Beyin Hatası" not in yanit

    def test_timeout_mesaji(self, ornek_config, ornek_mesajlar):
        """Timeout hatasi."""
        with patch.object(Beyin, "_cagir_openai_uyumlu",
                          side_effect=RuntimeError("Connection timed out")):
            beyin = Beyin(config=ornek_config)
            yanit = beyin.dusun("Sistem", ornek_mesajlar)
        assert self._yanit_beklenen_hata_iceriyor(yanit)

    def test_403_forbidden(self, ornek_config, ornek_mesajlar):
        """403 hatasi."""
        with patch.object(Beyin, "_cagir_openai_uyumlu",
                          side_effect=RuntimeError("403 Forbidden")):
            beyin = Beyin(config=ornek_config)
            yanit = beyin.dusun("Sistem", ornek_mesajlar)
        assert self._yanit_beklenen_hata_iceriyor(yanit)


# ── uret_v2() Fonksiyon Cagrisi Testleri ────────────────────────────────────

class TestUretV2:
    """Beyin.uret_v2() — native function calling."""

    def test_uret_v2_success(self, ornek_config, ornek_mesajlar):
        """uret_v2() tools olmadan basarili cagri."""
        with patch.object(Beyin, "_cagir_openai_uyumlu_v2", return_value={
            "role": "assistant", "content": "Selam!", "tool_calls": [],
        }):
            beyin = Beyin(config=ornek_config)
            sonuc = beyin.uret_v2("Sistem", ornek_mesajlar)
            assert sonuc["role"] == "assistant"
            assert sonuc["content"] == "Selam!"
            assert sonuc["tool_calls"] == []

    def test_uret_v2_with_tools(self, ornek_config, ornek_mesajlar):
        """uret_v2() tools parametresi ile."""
        with patch.object(Beyin, "_cagir_openai_uyumlu_v2", return_value={
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {"name": "HESAPLA", "arguments": '{"x":2,"y":3}'},
                }
            ],
        }):
            tools = [{"type": "function", "function": {"name": "HESAPLA", "parameters": {}}}]
            beyin = Beyin(config=ornek_config)
            sonuc = beyin.uret_v2("Sistem", ornek_mesajlar, tools=tools)
            assert len(sonuc["tool_calls"]) == 1
            assert sonuc["tool_calls"][0]["function"]["name"] == "HESAPLA"

    def test_uret_v2_tools_fallback(self, ornek_config, ornek_mesajlar):
        """Tools desteklenmiyorsa (400) -> tools'suz fallback."""
        cagrilan = []
        def mock_v2(*args, **kwargs):
            cagrilan.append(1)
            tools_arg = kwargs.get("tools")
            if len(cagrilan) == 1 and tools_arg:
                raise RuntimeError("400 Bad Request")
            return {"role": "assistant", "content": "Tools'suz yanit", "tool_calls": []}

        tools = [{"type": "function", "function": {"name": "TEST", "parameters": {}}}]
        with patch.object(Beyin, "_cagir_openai_uyumlu_v2", side_effect=mock_v2):
            beyin = Beyin(config=ornek_config)
            sonuc = beyin.uret_v2("Sistem", ornek_mesajlar, tools=tools)
            assert sonuc["content"] == "Tools'suz yanit"


# ── Yardimci Metod Testleri ──────────────────────────────────────────────────

class TestYardimciMetodlar:
    """Beyin._rate_limit_mi, _anahtar_bul vb."""

    def test_rate_limit_429(self, ornek_config):
        """_rate_limit_mi() 429 hatasini taniyor mu?"""
        beyin = Beyin(config=ornek_config)
        import requests
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        hata = requests.HTTPError(response=mock_resp)
        assert beyin._rate_limit_mi(hata)

    def test_rate_limit_mesaj(self, ornek_config):
        """_rate_limit_mi() hata mesajinda 'rate limit' gecenleri taniyor."""
        beyin = Beyin(config=ornek_config)
        hata = RuntimeError("Rate limit exceeded")
        assert beyin._rate_limit_mi(hata)

    def test_rate_limit_diger_hata(self, ornek_config):
        """_rate_limit_mi() 500'u rate limit olarak gormez."""
        beyin = Beyin(config=ornek_config)
        import requests
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        hata = requests.HTTPError(response=mock_resp)
        assert not beyin._rate_limit_mi(hata)

    def test_fc_destekleniyor_varsayilan(self, ornek_config):
        """fc_destekleniyor() ilk cagrida True donduruyor mu?"""
        beyin = Beyin(config=ornek_config)
        assert beyin.fc_destekleniyor() is True

    def test_uretil_alias(self, ornek_config, ornek_mesajlar):
        """uret() alias'i dusun()'a yonlendiriyor mu?"""
        with patch.object(Beyin, "_cagir_openai_uyumlu", return_value="Alias test"):
            beyin = Beyin(config=ornek_config)
            yanit = beyin.uret("Sistem", ornek_mesajlar)
            assert yanit == "Alias test"
