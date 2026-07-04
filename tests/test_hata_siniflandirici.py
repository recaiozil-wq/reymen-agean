# -*- coding: utf-8 -*-
"""Testler: reymen.cereyan.hata_siniflandirici"""

import pytest
from reymen.cereyan.hata_siniflandirici import (
    api_hatasini_siniflandir,
    classify_api_error,
    FailoverReason,
    SiniflandirilmisHata,
)


# ── Yardımcı hata yaratıcıları ──────────────────────────────────────────────


def _http_hata(status: int, mesaj: str = "") -> Exception:
    """Basit HTTP hata simülatörü — status_code attribute'u olan exception."""

    class FakeHTTPError(Exception):
        pass

    e = FakeHTTPError(mesaj or f"HTTP {status}")
    e.status_code = status  # type: ignore[attr-defined]
    return e


def _body_hata(status: int, hata_mesaji: str = "", hata_kodu: str = "") -> Exception:
    """body attribute'u olan hata — SDK tarzı."""

    class FakeAPIError(Exception):
        pass

    e = FakeAPIError(f"HTTP {status}: {hata_mesaji}")
    e.status_code = status  # type: ignore[attr-defined]
    govde: dict = {}
    if hata_mesaji or hata_kodu:
        govde["error"] = {}
        if hata_mesaji:
            govde["error"]["message"] = hata_mesaji
        if hata_kodu:
            govde["error"]["code"] = hata_kodu
    e.body = govde  # type: ignore[attr-defined]
    return e


# ── FailoverReason enum testleri ─────────────────────────────────────────────


class TestFailoverReasonEnum:
    def test_tum_degerler_mevcut(self):
        assert FailoverReason.auth is not None
        assert FailoverReason.billing is not None
        assert FailoverReason.rate_limit is not None
        assert FailoverReason.context_overflow is not None
        assert FailoverReason.unknown is not None

    def test_value_stringler(self):
        assert FailoverReason.auth.value == "auth"
        assert FailoverReason.billing.value == "billing"
        assert FailoverReason.timeout.value == "timeout"

    def test_toplam_deger_sayisi(self):
        # Minimum beklenen değer sayısı
        assert len(list(FailoverReason)) >= 15


# ── SiniflandirilmisHata dataclass testleri ──────────────────────────────────


class TestSiniflandirilmisHata:
    def test_varsayilan_degerler(self):
        s = SiniflandirilmisHata(neden=FailoverReason.unknown)
        assert s.neden == FailoverReason.unknown
        assert s.durum_kodu is None
        assert s.yeniden_denenebilir is True
        assert s.sikistirilmali is False
        assert s.kimlik_dondurmeli is False
        assert s.fallback_olmali is False

    def test_hermes_uyumlu_propertyler(self):
        """ReYMeN ClassifiedError API uyumluluğu."""
        s = SiniflandirilmisHata(
            neden=FailoverReason.billing,
            yeniden_denenebilir=False,
            kimlik_dondurmeli=True,
            fallback_olmali=True,
        )
        assert s.reason == FailoverReason.billing
        assert s.retryable is False
        assert s.should_rotate_credential is True
        assert s.should_fallback is True
        assert s.should_compress is False

    def test_auth_property(self):
        s = SiniflandirilmisHata(neden=FailoverReason.auth)
        assert s.is_auth is True
        s2 = SiniflandirilmisHata(neden=FailoverReason.billing)
        assert s2.is_auth is False

    def test_classify_api_error_alias(self):
        """classify_api_error, api_hatasini_siniflandir ile aynı fonksiyon."""
        assert classify_api_error is api_hatasini_siniflandir


# ── Temel durum kodu sınıflandırmaları ───────────────────────────────────────


class TestDurumKoduSiniflandirma:
    def test_401_auth(self):
        s = api_hatasini_siniflandir(_http_hata(401))
        assert s.neden == FailoverReason.auth
        assert s.kimlik_dondurmeli is True
        assert s.yeniden_denenebilir is False

    def test_402_billing(self):
        s = api_hatasini_siniflandir(_body_hata(402, "insufficient credits"))
        assert s.neden == FailoverReason.billing
        assert s.kimlik_dondurmeli is True
        assert s.yeniden_denenebilir is False

    def test_402_gecici_kullanim_limiti_rate_limit(self):
        s = api_hatasini_siniflandir(
            _body_hata(402, "usage limit exceeded — retry after 60s")
        )
        assert s.neden == FailoverReason.rate_limit
        assert s.yeniden_denenebilir is True

    def test_403_auth(self):
        s = api_hatasini_siniflandir(_http_hata(403, "forbidden"))
        assert s.neden == FailoverReason.auth

    def test_429_rate_limit(self):
        s = api_hatasini_siniflandir(_http_hata(429, "Too Many Requests"))
        assert s.neden == FailoverReason.rate_limit
        assert s.yeniden_denenebilir is True

    def test_500_sunucu_hatasi(self):
        s = api_hatasini_siniflandir(_http_hata(500))
        assert s.neden == FailoverReason.server_error
        assert s.yeniden_denenebilir is True

    def test_503_asiri_yuklu(self):
        s = api_hatasini_siniflandir(_http_hata(503))
        assert s.neden == FailoverReason.overloaded
        assert s.yeniden_denenebilir is True

    def test_413_payload_cok_buyuk(self):
        s = api_hatasini_siniflandir(_http_hata(413))
        assert s.neden == FailoverReason.payload_too_large
        assert s.sikistirilmali is True

    def test_404_model_bulunamadi(self):
        s = api_hatasini_siniflandir(_body_hata(404, "model not found"))
        assert s.neden == FailoverReason.model_not_found
        assert s.fallback_olmali is True


# ── 400 sınıflandırma ayrıntıları ────────────────────────────────────────────


class TestDortYuzSiniflandirma:
    def test_400_context_tasma(self):
        s = api_hatasini_siniflandir(_body_hata(400, "context length exceeded"))
        assert s.neden == FailoverReason.context_overflow
        assert s.sikistirilmali is True

    def test_400_gorsel_cok_buyuk(self):
        s = api_hatasini_siniflandir(_body_hata(400, "image too large"))
        assert s.neden == FailoverReason.image_too_large

    def test_400_multimodal_arac(self):
        s = api_hatasini_siniflandir(
            _body_hata(400, "tool message content must be a string")
        )
        assert s.neden == FailoverReason.multimodal_tool_content_unsupported

    def test_400_sifreli_icerik(self):
        s = api_hatasini_siniflandir(
            _body_hata(400, "invalid_encrypted_content", "invalid_encrypted_content")
        )
        assert s.neden == FailoverReason.invalid_encrypted_content

    def test_400_dusunme_imzasi(self):
        e = _body_hata(400, "thinking block signature cannot be modified")
        s = api_hatasini_siniflandir(e)
        assert s.neden == FailoverReason.thinking_signature

    def test_400_bilinmeyen_parametre_format_hatasi(self):
        s = api_hatasini_siniflandir(
            _body_hata(400, "unknown parameter: stream_options")
        )
        assert s.neden == FailoverReason.format_error


# ── Mesaj örüntüsü sınıflandırmaları ─────────────────────────────────────────


class TestMesajOrnekSiniflandirma:
    def test_faturalama_ornegi(self):
        s = api_hatasini_siniflandir(Exception("insufficient credits"))
        assert s.neden == FailoverReason.billing

    def test_rate_limit_ornegi(self):
        # "rate limit" tek başına → rate_limit; "rate limit exceeded" → billing
        # (çünkü "limit exceeded" → _KULLANIM_LIMITI_ORNEKLERI'ne takılır)
        s = api_hatasini_siniflandir(Exception("too many requests — rate limit hit"))
        assert s.neden == FailoverReason.rate_limit

    def test_context_overflow_ornegi(self):
        s = api_hatasini_siniflandir(Exception("context window exceeded"))
        assert s.neden == FailoverReason.context_overflow

    def test_auth_ornegi(self):
        s = api_hatasini_siniflandir(Exception("invalid api key"))
        assert s.neden == FailoverReason.auth

    def test_model_bulunamadi_ornegi(self):
        s = api_hatasini_siniflandir(Exception("model not found: gpt-5"))
        assert s.neden == FailoverReason.model_not_found

    def test_zaman_asimi_ornegi(self):
        s = api_hatasini_siniflandir(Exception("request timed out"))
        assert s.neden == FailoverReason.timeout
        assert s.yeniden_denenebilir is True

    def test_icerik_politikasi_ornegi(self):
        s = api_hatasini_siniflandir(Exception("violates our usage policies"))
        assert s.neden == FailoverReason.content_policy_blocked
        assert s.yeniden_denenebilir is False

    def test_provider_politikasi_ornegi(self):
        s = api_hatasini_siniflandir(
            Exception("no endpoints available matching your guardrail")
        )
        assert s.neden == FailoverReason.provider_policy_blocked


# ── Transport / timeout testleri ─────────────────────────────────────────────


class TestTransportHatalar:
    def test_timeout_tipi(self):
        e = TimeoutError("connection timed out")
        s = api_hatasini_siniflandir(e)
        assert s.neden == FailoverReason.timeout

    def test_connection_error_tipi(self):
        e = ConnectionError("connection refused")
        s = api_hatasini_siniflandir(e)
        assert s.neden == FailoverReason.timeout

    def test_ssl_gecici_hata(self):
        s = api_hatasini_siniflandir(Exception("[SSL: BAD_RECORD_MAC]"))
        assert s.neden == FailoverReason.timeout

    def test_bilinmeyen_hata_retry(self):
        s = api_hatasini_siniflandir(Exception("some random unexpected error"))
        assert s.neden == FailoverReason.unknown
        assert s.yeniden_denenebilir is True


# ── Provider parametresi ─────────────────────────────────────────────────────


class TestProviderParametresi:
    def test_provider_ve_model_aktarilir(self):
        s = api_hatasini_siniflandir(
            _http_hata(429),
            provider="deepseek",
            model="deepseek-chat",
        )
        assert s.provider == "deepseek"
        assert s.model == "deepseek-chat"
        assert s.neden == FailoverReason.rate_limit

    def test_context_uzunlugu_buyuk_oturum_context_overflow(self):
        """Büyük oturum + büyük payload → context overflow."""
        s = api_hatasini_siniflandir(
            _http_hata(400, ""),
            yaklasik_token=150_000,
            context_uzunlugu=200_000,
        )
        assert s.neden in {FailoverReason.context_overflow, FailoverReason.format_error}


# ── Özgün Anthropic özel durumlar ────────────────────────────────────────────


class TestAnthropicOzelDurumlar:
    def test_uzun_context_katmani(self):
        e = _body_hata(429, "extra usage long context tier")
        s = api_hatasini_siniflandir(e)
        assert s.neden == FailoverReason.long_context_tier
        assert s.sikistirilmali is True

    def test_llama_cpp_gramer(self):
        e = _body_hata(400, "error parsing grammar: json-schema-to-grammar failed")
        s = api_hatasini_siniflandir(e)
        assert s.neden == FailoverReason.llama_cpp_grammar_pattern

    def test_403_faturalama_key_limit(self):
        e = _body_hata(403, "key limit exceeded for this month")
        s = api_hatasini_siniflandir(e)
        assert s.neden == FailoverReason.billing
        assert s.kimlik_dondurmeli is True
