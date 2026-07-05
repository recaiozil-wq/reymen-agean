# -*- coding: utf-8 -*-
"""
beyin.py â€” Multi-provider LLM connection layer.

Supported providers:
    LM Studio Â· DeepSeek Â· OpenAI Â· Anthropic Â· Groq Â· Azure OpenAI
    AWS Bedrock Â· Google Gemini / Vertex AI Â· Moonshot Â· Ollama

Integrated modules (optional):
    credential_pool   â€” API key pool
    prompt_caching    â€” Prompt caching
    nous_rate_guard   â€” Rate limiter
    providers         â€” Provider registry
    account_usage     â€” Usage tracking
    akilli_yonlendirici â€” Task-based model routing
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Generator, List, Optional, Tuple

import requests

# â”€â”€ Provider Abstraction (config.yaml model.provider okur) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
try:
    from reymen.cereyan.provider_abstraction import (
        ProviderBase,
        get_provider,
        saglayiciyi_yapilandir,
        ProviderYanit,
        _VARSAYILAN_MODELLER as _PA_VARSAYILAN_MODELLER,
    )

    _PA_AKTIF = True
except ImportError:
    _PA_AKTIF = False
    ProviderBase = None  # type: ignore[assignment, misc]
    get_provider = None  # type: ignore[assignment]
    saglayiciyi_yapilandir = None  # type: ignore[assignment]

# â”€â”€ Observability / Tracing (opsiyonel) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
try:
    from reymen.core.observability import trace_llm_call

    _TRACE_LLM_AKTIF = True
except ImportError:
    # Observability modülü yoksa no-op dekoratör
    def trace_llm_call(span_adi=None, attributes=None):
        def decorator(func):
            return func

        return decorator

    _TRACE_LLM_AKTIF = False

# â”€â”€ Modül düzeyinde logger â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
logger = logging.getLogger(__name__)

# â”€â”€ Sabitler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
TIMEOUT_SANIYE: int = 300
_VARSAYILAN_MAX_TOKEN: int = 4096
_VARSAYILAN_SICAKLIK: float = 0.7


# â”€â”€ Hata sÄ±nÄ±flandÄ±rÄ±cÄ± (opsiyonel) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
try:
    from reymen.cereyan.hata_siniflandirici import (
        api_hatasini_siniflandir as _api_hatasini_siniflandir,
        FailoverReason as _FailoverReason,
    )

    _HATA_SINIF_AKTIF = True
except ImportError:
    _api_hatasini_siniflandir = None  # type: ignore[assignment]
    _FailoverReason = None  # type: ignore[assignment]
    _HATA_SINIF_AKTIF = False

# â”€â”€ Opsiyonel modül yükleyici â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _guvensiz_import(modul_adi: str) -> Any:
    """Modülü içe aktar; bulunamazsa None döndür (hata yükseltme)."""
    try:
        import importlib

        return importlib.import_module(modul_adi)
    except Exception:
        return None


_credential_pool = _guvensiz_import(
    "reymen.sistem.credential_persistence"
) or _guvensiz_import("reymen.sistem.credential_pool")
_prompt_caching = _guvensiz_import("reymen.arac.prompt_caching")
_nous_rate_guard = _guvensiz_import("reymen.guvenlik.nous_rate_guard")
_providers_registry = _guvensiz_import("reymen.sistem.providers")

_POOL_AKTIF = _credential_pool is not None
_CACHE_AKTIF = _prompt_caching is not None
_GUARD_AKTIF = (
    _nous_rate_guard is not None
    and hasattr(_nous_rate_guard, "rate_guard_izin_ver")
    and hasattr(_nous_rate_guard, "rate_guard_basla")
    and hasattr(_nous_rate_guard, "rate_guard_bitir")
)
_REGISTRY_AKTIF = _providers_registry is not None


# â”€â”€ Veri yapÄ±larÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


@dataclass
class SaglayCiAdim:
    """Fallback zincirindeki tek bir saÄŸlayÄ±cÄ± adÄ±mÄ±."""

    provider: str
    model: str
    base_url: str
    api_key: str

    def __repr__(self) -> str:  # noqa: D105
        return f"<SaglayCiAdim provider={self.provider!r} model={self.model!r}>"


@dataclass
class LLMYanitMeta:
    """_cagir() dönüÅŸ deÄŸeri: metin + basit üstveri."""

    metin: str
    provider: str
    model: str
    sure_sn: float = 0.0
    tahmini_token: int = 0


# â”€â”€ SaÄŸlayÄ±cÄ± varsayÄ±lan modelleri â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_VARSAYILAN_MODELLER: dict[str, str] = {
    "deepseek": "deepseek-chat",
    "openai": "gpt-4o-mini",
    "anthropic": "claude-haiku-4-5-20251001",
    "groq": "llama-3.1-8b-instant",
    "ollama": "llama3.1:8b",
    "moonshot": "moonshot-v1-8k",
    "azure": "",  # env'den okunur
    "bedrock": "",  # env'den okunur
    "gemini": "gemini-1.5-flash",
    "gemini_cloud": "gemini-1.5-flash",
    "openrouter": "deepseek/deepseek-chat",
    "lmstudio_reasoning": "",  # env'den okunur
    "codex_responses": "",  # env'den okunur
    # â”€â”€ Yeni OpenAI-uyumlu saÄŸlayÄ±cÄ±lar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "together": "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "fireworks": "accounts/fireworks/models/llama-v3p1-8b-instruct",
    "mistral": "mistral-small-latest",
    "cohere": "command-r-plus",
    "perplexity": "llama-3.1-sonar-small-128k-online",
}

# Provider â†’ env deÄŸiÅŸken adlarÄ±
_PROVIDER_ENV: dict[str, str] = {
    "deepseek": "DEEPSEEK_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "groq": "GROQ_API_KEY",
    "moonshot": "MOONSHOT_API_KEY",
    "azure": "AZURE_OPENAI_API_KEY",
    "bedrock": "AWS_ACCESS_KEY_ID",
    "gemini": "GEMINI_API_KEY",
    "gemini_cloud": "GEMINI_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    # â”€â”€ Yeni OpenAI-uyumlu saÄŸlayÄ±cÄ±lar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "together": "TOGETHER_API_KEY",
    "fireworks": "FIREWORKS_API_KEY",
    "mistral": "MISTRAL_API_KEY",
    "cohere": "COHERE_API_KEY",
    "perplexity": "PERPLEXITY_API_KEY",
}


# â”€â”€ Ana sÄ±nÄ±f â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


class Beyin:
    """Ã‡ok-saÄŸlayÄ±cÄ±lÄ± LLM baÄŸlantÄ± katmanÄ±.

    Ã–zellikler:
        * Otomatik fallback zinciri â€” birincil saÄŸlayÄ±cÄ± baÅŸarÄ±sÄ±z olursa
          yapÄ±landÄ±rmadaki diÄŸer saÄŸlayÄ±cÄ±lar sÄ±rayla denenir.
        * Rate-limit yeniden deneme â€” exponential backoff ile.
        * Ä°ptal edilebilir API çaÄŸrÄ±larÄ± â€” iptal_et() / sifirla() API'si.
        * Streaming desteÄŸi â€” dusun_stream() generator arayüzü.
        * Opsiyonel entegrasyonlar: credential_pool, prompt_caching,
          nous_rate_guard, account_usage.

    Args:
        config: SaÄŸlayÄ±cÄ± yapÄ±landÄ±rma sözlüÄŸü.  Beklenen alanlar::

            {
                "default_provider": "lmstudio",
                "default_model":    "model-adÄ±",
                "providers": {
                    "lmstudio": {"base_url": "http://localhost:1234", "api_key": ""},
                    "deepseek": {"base_url": "https://api.deepseek.com", "api_key": "sk-..."},
                },
                "fallback_model": None  # ya da {"provider": ..., "model": ..., ...}
            }
    """

    # â”€â”€ Rate-limit yeniden deneme parametreleri â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    MAKS_DENEME: int = 3
    ILK_BEKLEME: float = 1.0
    BEKLEME_CARPAN: float = 2.0

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        # model.provider oku (config.yaml model: provider: deepseek)
        model_blok = config.get("model", {})
        if isinstance(model_blok, dict):
            model_provider = model_blok.get("provider", "")
            model_model = model_blok.get("model") or model_blok.get("default", "")
        else:
            model_provider = ""
            model_model = ""

        # Ã–nce üst düzey anahtarlarÄ±, yoksa "general" altÄ±ndakileri oku
        self.provider: str = model_provider or config.get(
            "default_provider",
            config.get("general", {}).get("default_provider", "lmstudio"),
        )
        self.model: str = model_model or config.get(
            "default_model",
            config.get("general", {}).get(
                "default_model",
                "cognitivecomputations.dolphin3.0-llama3.1-8b",
            ),
        )

        self.base_url, self.api_key = self._saglayici_baglantisi_kur(self.provider)

        # Ä°ptal olayÄ± â€” _zincir_insa_et() öncesinde oluÅŸturulmalÄ±
        self._iptal_olayi = threading.Event()
        self._fallback_zinciri: list[SaglayCiAdim] = self._zincir_insa_et()
        # Instance-level FC cache (class attr'dan baÄŸÄ±msÄ±z â€” test izolasyonu)
        self._fc_desteklenmeyen: set = set()

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # BaÅŸlatma yardÄ±mcÄ±larÄ±
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _saglayici_baglantisi_kur(self, provider: str) -> Tuple[str, str]:
        """base_url ve api_key deÄŸerlerini döndürür."""
        prov_conf = self.config.get("providers", {}).get(provider, {})

        # SaÄŸlayÄ±cÄ± kayÄ±t defterinden varsayÄ±lan base_url
        if _REGISTRY_AKTIF:
            profil = _providers_registry.get_provider_profile(provider)  # type: ignore[union-attr]
            base_url = prov_conf.get("base_url") or (
                profil.base_url if profil else "http://localhost:1234"
            )
        else:
            base_url = prov_conf.get("base_url", "http://localhost:1234")

        api_key = self._anahtar_bul(provider, prov_conf)
        return base_url, api_key

    def _anahtar_bul(self, provider: str, prov_conf: dict) -> str:
        """API anahtarÄ±nÄ± ÅŸu sÄ±rayla arar: credential_pool â†’ config â†’ os.environ.

        Args:
            provider:  SaÄŸlayÄ±cÄ± adÄ± (ör. "openai").
            prov_conf: config["providers"][provider] sözlüÄŸü.

        Returns:
            Bulunan anahtar ya da lmstudio için "not-needed", diÄŸerleri için "".
        """
        env_adi = _PROVIDER_ENV.get(provider)

        # 1. credential_pool
        if _POOL_AKTIF and env_adi:
            try:
                if hasattr(_credential_pool, "anahtar_al"):
                    deger = _credential_pool.anahtar_al(env_adi)  # type: ignore[union-attr]
                    if deger:
                        return deger
            except Exception as _e:
                logger.warning("[Beyin] except Exception (L240): %s", Exception)
                pass

        # 2. config
        deger = prov_conf.get("api_key", "")
        if deger and not deger.startswith("***"):
            return deger

        # 3. os.environ
        if env_adi:
            deger = os.environ.get(env_adi, "")
            if deger and not deger.startswith("***"):
                return deger

        return "not-needed" if provider == "lmstudio" else ""

    def _varsayilan_model(self, provider: str) -> str:
        """Provider için varsayÄ±lan model adÄ±nÄ± döndürür."""
        env_degerleri: dict[str, str] = {
            "azure": os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
            "bedrock": os.environ.get(
                "BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0"
            ),
            "lmstudio_reasoning": os.environ.get(
                "LMSTUDIO_MODEL", "cognitivecomputations.dolphin3.0-llama3.1-8b"
            ),
            "codex_responses": os.environ.get("OPENAI_CODEX_MODEL", "o4-mini"),
        }
        if provider in env_degerleri:
            return env_degerleri[provider]
        return _VARSAYILAN_MODELLER.get(provider, "default")

    def _zincir_insa_et(self) -> list[SaglayCiAdim]:
        """Fallback saÄŸlayÄ±cÄ± zincirini oluÅŸturur.

        SÄ±ra: birincil â†’ fallback_model â†’ anahtarÄ± geçerli diÄŸer saÄŸlayÄ±cÄ±lar.
        """
        zincir: list[SaglayCiAdim] = [
            SaglayCiAdim(
                provider=self.provider,
                model=self.model,
                base_url=self.base_url,
                api_key=self.api_key,
            )
        ]

        # AçÄ±kça tanÄ±mlÄ± fallback model
        fb = self.config.get("fallback_model")
        if fb and isinstance(fb, dict):
            key = fb.get("api_key", "")
            if key and not key.startswith("***"):
                zincir.append(
                    SaglayCiAdim(
                        provider=fb.get("provider", "openai"),
                        model=fb.get("model", "gpt-4o-mini"),
                        base_url=fb.get("base_url", ""),
                        api_key=key,
                    )
                )

        # YapÄ±landÄ±rmadaki diÄŸer saÄŸlayÄ±cÄ±lar
        for pname, pconf in self.config.get("providers", {}).items():
            if pname == self.provider:
                continue
            key = self._anahtar_bul(pname, pconf)
            if key and not key.startswith("***") and key != "not-needed":
                zincir.append(
                    SaglayCiAdim(
                        provider=pname,
                        model=self._varsayilan_model(pname),
                        base_url=pconf.get("base_url", ""),
                        api_key=key,
                    )
                )

        return zincir

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Ä°ptal mekanizmasÄ±
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def iptal_et(self) -> None:
        """Devam eden API çaÄŸrÄ±sÄ±nÄ± iptal et (ReYMeN interruptible API pattern)."""
        self._iptal_olayi.set()

    def sifirla(self) -> None:
        """Ä°ptal olayÄ±nÄ± sÄ±fÄ±rla â€” yeni görev baÅŸlamadan önce çaÄŸÄ±r."""
        self._iptal_olayi.clear()

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Hata yardÄ±mcÄ±larÄ±
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    @staticmethod
    def _rate_limit_mi(hata: Exception) -> bool:
        """HTTP 429 / 'rate limit' içerikli hata mÄ±?"""
        mesaj = str(hata).lower()
        if any(k in mesaj for k in ("429", "rate limit", "too many requests")):
            return True
        try:
            resp = getattr(hata, "response", None)
            if resp is not None:
                return resp.status_code == 429
        except Exception as _e:
            logger.warning("[Beyin] except Exception (L323): %s", Exception)
            pass
        return False

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Ã‡aÄŸrÄ± katmanlarÄ±: retry â†’ interruptible â†’ provider dispatch
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _cagir_ile_retry(
        self,
        adim: SaglayCiAdim,
        sistem_prompt: str,
        mesajlar: list[dict],
    ) -> str:
        """Rate-limit hatasÄ±nda exponential backoff ile yeniden dener.

        402/403/401 hatlarÄ± retry edilmez â€” hemen fallback zincirine geçilir.
        """
        bekleme = self.ILK_BEKLEME
        son_hata: Exception | None = None

        for deneme in range(1, self.MAKS_DENEME + 1):
            try:
                meta = self._cagir(adim, sistem_prompt, mesajlar)
                return meta.metin
            except Exception as hata:
                son_hata = hata
                hata_str = str(hata)
                # 402/403/401 â€” retry edilemez, hemen fallback'a git
                if any(
                    k in hata_str
                    for k in (
                        "402",
                        "403",
                        "401",
                        "Payment Required",
                        "Forbidden",
                        "Unauthorized",
                    )
                ):
                    logger.warning(
                        "[Beyin] %s â€” retry edilmiyor, fallback'a geçiliyor.",
                        adim.provider,
                    )
                    raise
                if self._rate_limit_mi(hata) and deneme < self.MAKS_DENEME:
                    logger.warning(
                        "[Beyin] Rate limit â€” %.1fs bekleniyor (%d/%d)â€¦",
                        bekleme,
                        deneme,
                        self.MAKS_DENEME - 1,
                    )
                    time.sleep(bekleme)
                    bekleme *= self.BEKLEME_CARPAN
                else:
                    raise

    def _kesintibilir_cagir(
        self,
        adim: SaglayCiAdim,
        sistem_prompt: str,
        mesajlar: list[dict],
    ) -> str:
        """API çaÄŸrÄ±sÄ±nÄ± arka plan thread'inde çalÄ±ÅŸtÄ±r; iptal olayÄ± set edilirse kes.

        Ana thread iptal olayÄ±nÄ± izler; API thread'i arka planda çalÄ±ÅŸmaya devam
        eder ama sonucu görmezden gelinir (ReYMeN interruptible_api_call pattern).
        """
        sonuc_kabi: list[str | None] = [None]
        hata_kabi: list[Exception | None] = [None]
        tamam = threading.Event()

        def api_worker() -> None:
            try:
                sonuc_kabi[0] = self._cagir_ile_retry(adim, sistem_prompt, mesajlar)
            except Exception as e:
                hata_kabi[0] = e
            finally:
                tamam.set()

        t = threading.Thread(target=api_worker, daemon=True)
        t.start()

        while not tamam.wait(timeout=0.5):
            if self._iptal_olayi.is_set():
                raise InterruptedError(
                    "[Beyin] API çaÄŸrÄ±sÄ± kullanÄ±cÄ± tarafÄ±ndan iptal edildi."
                )

        if hata_kabi[0] is not None:
            raise hata_kabi[0]

        # sonuc_kabi[0] None olamaz; tip denetleyicisini yatÄ±ÅŸtÄ±r
        assert sonuc_kabi[0] is not None
        return sonuc_kabi[0]

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Genel yüksek-seviye arayüz
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    @trace_llm_call()
    def dusun(
        self,
        sistem_prompt: str,
        mesajlar: list[dict],
        model: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> str:
        """LLM'den yanÄ±t üret; fallback zincirine göre saÄŸlayÄ±cÄ±lar denenir.

        Args:
            sistem_prompt: Sistem talimatÄ±.
            mesajlar:      KonuÅŸma geçmiÅŸi ({"role": ..., "content": ...} listesi).
            model:         Ä°steÄŸe baÄŸlÄ± model geçersiz kÄ±lma.
            provider:      Ä°steÄŸe baÄŸlÄ± saÄŸlayÄ±cÄ± geçersiz kÄ±lma.

        Returns:
            LLM yanÄ±tÄ± metni ya da "[Beyin HatasÄ±] â€¦" hata dizesi.
        """
        # Tek seferlik saÄŸlayÄ±cÄ± geçersiz kÄ±lma
        if provider and provider != self.provider:
            return self._tek_seferlik_cagri(provider, model, sistem_prompt, mesajlar)

        # OpenRouter fallback hazÄ±rlÄ±ÄŸÄ±: zincirde yoksa eklenir
        openrouter_eklendi = False

        son_hata = ""
        for i, adim in enumerate(self._fallback_zinciri):
            try:
                t0 = time.monotonic()

                # Rate guard â€” izin kontrolü
                if _GUARD_AKTIF:
                    try:
                        if not _nous_rate_guard.rate_guard_izin_ver(adim.provider):  # type: ignore[union-attr]
                            logger.info(
                                "[RateGuard] %s hÄ±z sÄ±nÄ±rÄ± â€” atlanÄ±yor.", adim.provider
                            )
                            continue
                        _nous_rate_guard.rate_guard_basla(adim.provider)  # type: ignore[union-attr]
                    except AttributeError:
                        pass  # guard fonksiyonu eksik, LLM cagrisi yine de yapilsin

                # Prompt caching (yalnÄ±zca birincil saÄŸlayÄ±cÄ±)
                if _CACHE_AKTIF and i == 0:
                    sonuc = _prompt_caching.cache_ile_uret(  # type: ignore[union-attr]
                        sistem_prompt,
                        mesajlar,
                        lambda p, m: self._kesintibilir_cagir(adim, p, m),
                    )
                else:
                    sonuc = self._kesintibilir_cagir(adim, sistem_prompt, mesajlar)

                if _GUARD_AKTIF:
                    try:
                        _nous_rate_guard.rate_guard_bitir(adim.provider)  # type: ignore[union-attr]
                    except AttributeError as _e:
                        logger.warning(
                            "[Beyin] Nitelik hatasi (L462): %s", AttributeError
                        )
                        pass

                sure = time.monotonic() - t0
                if i > 0:
                    logger.info(
                        "[Beyin] Fallback #%d baÅŸarÄ±lÄ± (%s, %.1fs)",
                        i,
                        adim.provider,
                        sure,
                    )

                self._kullanim_kaydet(adim, sistem_prompt, mesajlar, sonuc)
                return sonuc

            except Exception as e:
                son_hata = str(e)
                # â”€â”€ Türkçe hata mesajÄ± çevirisi â”€â”€
                hata_str = str(e)
                if "402" in hata_str or "Payment Required" in hata_str:
                    turkce_hata = f"âŒ {adim.provider} kredisi bitti (402 Payment Required). HesabÄ±na kredi yüklemelisin."
                elif "401" in hata_str or "Unauthorized" in hata_str:
                    turkce_hata = f"âŒ {adim.provider} API anahtarÄ± geçersiz (401 Unauthorized). .env dosyasÄ±ndaki key'i kontrol et."
                elif (
                    "429" in hata_str
                    or "Rate limit" in hata_str
                    or "Too Many Requests" in hata_str
                ):
                    turkce_hata = f"â³ {adim.provider} hÄ±z sÄ±nÄ±rÄ± aÅŸÄ±ldÄ± (429). KÄ±sa süre bekle, otomatik düzelecek."
                elif "403" in hata_str or "Forbidden" in hata_str:
                    turkce_hata = f"ğŸš« {adim.provider} eriÅŸim reddedildi (403). API key izinlerini kontrol et."
                elif "500" in hata_str or "Internal Server Error" in hata_str:
                    turkce_hata = f"ğŸ”§ {adim.provider} sunucu hatasÄ± (500). SaÄŸlayÄ±cÄ±nÄ±n durumunu kontrol et."
                elif "timeout" in hata_str.lower() or "timed out" in hata_str.lower():
                    turkce_hata = f"â° {adim.provider} zaman aÅŸÄ±mÄ±. Ä°nternet baÄŸlantÄ±nÄ± kontrol et."
                else:
                    turkce_hata = f"âŒ {adim.provider} hatasÄ±: {e}"

                # OpenRouter fallback: 402/403/429 hatasÄ± varsa otomatik OpenRouter'a geç
                if not openrouter_eklendi and adim.provider != "openrouter":
                    if any(
                        k in hata_str
                        for k in (
                            "402",
                            "403",
                            "429",
                            "Payment Required",
                            "Forbidden",
                            "Rate limit",
                        )
                    ):
                        openrouter_key = self._anahtar_bul(
                            "openrouter",
                            self.config.get("providers", {}).get("openrouter", {}),
                        )
                        if openrouter_key and not openrouter_key.startswith("***"):
                            openrouter_base = (
                                self.config.get("providers", {})
                                .get("openrouter", {})
                                .get("base_url", "https://openrouter.ai/api")
                            )
                            openrouter_model = self._varsayilan_model("openrouter")
                            logger.info(
                                "[Beyin] %s hatasi â€” OpenRouter fallback deneniyor (%s)...",
                                adim.provider,
                                openrouter_model,
                            )
                            # OpenRouter adÄ±mÄ±nÄ± zincire EKLE (bu turda da dene)
                            self._fallback_zinciri.append(
                                SaglayCiAdim(
                                    provider="openrouter",
                                    model=openrouter_model,
                                    base_url=openrouter_base,
                                    api_key=openrouter_key,
                                )
                            )
                            openrouter_eklendi = True

                if self._rate_limit_mi(e):
                    logger.warning(
                        "[Beyin] Rate limit (%s) â€” sonraki saÄŸlayÄ±cÄ±ya geçiliyor.",
                        adim.provider,
                    )
                else:
                    logger.error("[Beyin] %s", turkce_hata)

                if _GUARD_AKTIF:
                    try:
                        _nous_rate_guard.rate_guard_bitir(adim.provider)  # type: ignore[union-attr]
                    except Exception:
                        logger.warning("[fix_01_sessiz_except] Exception")

        # â”€â”€ Tüm saÄŸlayÄ±cÄ±lar baÅŸarÄ±sÄ±z â€” Türkçe özet â”€â”€
        if "402" in son_hata:
            return "[Beyin HatasÄ±] âŒ Hiçbir saÄŸlayÄ±cÄ± çalÄ±ÅŸmÄ±yor. DeepSeek/OpenRouter kredisi bitmiÅŸ olabilir."
        elif "401" in son_hata:
            return "[Beyin HatasÄ±] âŒ Hiçbir saÄŸlayÄ±cÄ± çalÄ±ÅŸmÄ±yor. API anahtarlarÄ± geçersiz."
        elif "429" in son_hata:
            return "[Beyin HatasÄ±] â³ Tüm saÄŸlayÄ±cÄ±lar hÄ±z sÄ±nÄ±rÄ±nda. Biraz bekle tekrar dene."
        elif "timeout" in son_hata.lower():
            return "[Beyin HatasÄ±] â° Tüm saÄŸlayÄ±cÄ±larda zaman aÅŸÄ±mÄ±. Ä°nternet baÄŸlantÄ±nÄ± kontrol et."
        else:
            return f"[Beyin HatasÄ±] âŒ Tüm saÄŸlayÄ±cÄ±lar baÅŸarÄ±sÄ±z. Son hata: {son_hata}"

    def _tek_seferlik_cagri(
        self,
        provider: str,
        model: Optional[str],
        sistem_prompt: str,
        mesajlar: list[dict],
    ) -> str:
        """Geçici saÄŸlayÄ±cÄ± geçersiz kÄ±lmasÄ± için yardÄ±mcÄ±."""
        pconf = self.config.get("providers", {}).get(provider, {})
        adim = SaglayCiAdim(
            provider=provider,
            model=model or self._varsayilan_model(provider),
            base_url=pconf.get("base_url", ""),
            api_key=self._anahtar_bul(provider, pconf),
        )
        try:
            return self._cagir_ile_retry(adim, sistem_prompt, mesajlar)
        except Exception as e:
            return f"[Beyin HatasÄ±] {provider}: {e}"

    def uret(
        self,
        sistem_prompt: str,
        mesajlar: list[dict],
        **kwargs: Any,
    ) -> str:
        """dusun() için geriye dönük uyumlu alias."""
        return self.dusun(sistem_prompt, mesajlar)

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Native Function Calling (OpenAI tools schema)
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _cagir_openai_uyumlu_v2(
        self,
        base_url: str,
        api_key: str,
        model: str,
        sistem_prompt: str,
        mesajlar: list[dict],
        tools: Optional[list] = None,
    ) -> dict:
        """OpenAI-uyumlu tek API çaÄŸrÄ±sÄ±; tool_calls'Ä± ayrÄ±ÅŸtÄ±rÄ±r.

        Provider tools parametresini desteklemiyorsa tools olmadan yeniden dener
        (graceful degradation) ve sonucu tool_calls=[] ile döndürür.

        Returns:
            {"role": "assistant", "content": str, "tool_calls": list}
        """
        import requests as _req

        def _cagri_yap(with_tools: bool) -> dict:
            payload: dict = {
                "model": model,
                "messages": [{"role": "system", "content": sistem_prompt}] + mesajlar,
            }
            if with_tools and tools:
                payload["tools"] = tools
                payload["tool_choice"] = "auto"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            r = _req.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120,
            )
            r.raise_for_status()
            msg = r.json()["choices"][0]["message"]
            return {
                "role": "assistant",
                "content": msg.get("content") or "",
                "tool_calls": msg.get("tool_calls") or [],
            }

        _provider_key = f"{base_url}:{model}"
        _try_with_tools = tools and _provider_key not in self._fc_desteklenmeyen

        try:
            return _cagri_yap(with_tools=_try_with_tools)
        except Exception as e:
            _kod = getattr(getattr(e, "response", None), "status_code", None)
            if _try_with_tools and _kod in (400, 422):
                # Provider tools'u reddetti â†’ "no-fc" iÅŸaretle, tools'suz yeniden dene
                self._fc_desteklenmeyen.add(_provider_key)
                logger.info(
                    "[uret_v2] %s tools desteklemiyor (%s) â†’ fallback.", model, _kod
                )
                return _cagri_yap(with_tools=False)
            raise

    def fc_destekleniyor(self) -> bool:
        """Aktif provider'Ä±n native function calling'i destekleyip desteklemediÄŸini döndürür.

        Ä°lk çaÄŸrÄ±da bilinmez (True döner â€” dene ve öÄŸren). BaÅŸarÄ±sÄ±z olursa
        _fc_desteklenmeyen cache'ine eklenir ve False döner.
        """
        _key = f"{self.base_url}:{self.model}"
        return _key not in self._fc_desteklenmeyen

    @trace_llm_call()
    def uret_v2(
        self,
        sistem_prompt: str,
        mesajlar: list[dict],
        tools: Optional[list] = None,
    ) -> dict:
        """Native function calling destekli LLM çaÄŸrÄ±sÄ±.

        Fallback zincirini dener; tüm provider'lar baÅŸarÄ±sÄ±z olursa
        tools olmadan metin üretir ve tool_calls=[] ile döner.

        Returns:
            {"role": "assistant", "content": str, "tool_calls": list}
        """
        _son_hata: Optional[Exception] = None
        for adim in self._fallback_zinciri:
            try:
                return self._cagir_openai_uyumlu_v2(
                    adim.base_url,
                    adim.api_key,
                    adim.model,
                    sistem_prompt,
                    mesajlar,
                    tools=tools,
                )
            except Exception as e:
                _son_hata = e
                # GeliÅŸmiÅŸ sÄ±nÄ±flandÄ±rÄ±cÄ±yla karar ver
                if _HATA_SINIF_AKTIF and _api_hatasini_siniflandir is not None:
                    try:
                        sinif = _api_hatasini_siniflandir(
                            e, provider=adim.provider, model=adim.model
                        )
                        neden = sinif.neden
                        logger.debug(
                            "[uret_v2] %s baÅŸarÄ±sÄ±z (neden=%s, retry=%s): %s",
                            adim.provider,
                            neden.value,
                            sinif.yeniden_denenebilir,
                            e,
                        )
                        # Ä°çerik politikasÄ± ihlali â†’ fallback dene ama zinciri de kÄ±r
                        if neden == _FailoverReason.content_policy_blocked:
                            logger.warning(
                                "[uret_v2] Ä°çerik politikasÄ± ihlali (%s) â€” metin fallback.",
                                adim.provider,
                            )
                            break
                        # Context overflow â†’ tools olmadan denemeye devam et
                        if neden == _FailoverReason.context_overflow:
                            logger.warning(
                                "[uret_v2] Context overflow (%s) â€” sÄ±kÄ±ÅŸtÄ±rma gerekebilir.",
                                adim.provider,
                            )
                    except Exception:
                        logger.debug("[uret_v2] %s baÅŸarÄ±sÄ±z: %s", adim.provider, e)
                else:
                    logger.debug("[uret_v2] %s baÅŸarÄ±sÄ±z: %s", adim.provider, e)
                continue
        # Tüm provider'lar baÅŸarÄ±sÄ±z â†’ metin fallback
        logger.warning(
            "[uret_v2] Tüm provider'lar baÅŸarÄ±sÄ±z (%s) â†’ metin moduna geçildi.",
            _son_hata,
        )
        metin = self.dusun(sistem_prompt, mesajlar)
        return {"role": "assistant", "content": metin or "", "tool_calls": []}

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Streaming arayüzü
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def dusun_stream(
        self,
        sistem_prompt: str,
        mesajlar: list[dict],
        model: Optional[str] = None,
    ) -> Generator[str, None, None]:
        """Streaming LLM yanÄ±tÄ± â€” token token yield eder.

        OpenAI-uyumlu saÄŸlayÄ±cÄ±lar (LM Studio, Ollama, DeepSeek, Groq vb.)
        ve Anthropic desteklenir. DiÄŸer saÄŸlayÄ±cÄ±larda tam yanÄ±t tek seferde
        yield edilir (graceful degrade).

        KullanÄ±m::

            for token in beyin.dusun_stream(sistem_prompt, mesajlar):
                print(token, end="", flush=True)

        Yields:
            str: Bir token veya küçük metin parçasÄ±.
        """
        aktif_model = model or self.model

        if self.provider == "anthropic":
            try:
                yield from self._stream_anthropic(
                    self.api_key, aktif_model, sistem_prompt, mesajlar
                )
            except Exception as e:
                logger.warning(
                    "[Beyin] Anthropic stream baÅŸarÄ±sÄ±z, tam yanÄ±ta düÅŸülüyor: %s", e
                )
                yield self.dusun(sistem_prompt, mesajlar, model=model)
            return

        try:
            yield from self._stream_openai_uyumlu(
                self.base_url, self.api_key, aktif_model, sistem_prompt, mesajlar
            )
        except Exception as e:
            logger.warning("[Beyin] Streaming baÅŸarÄ±sÄ±z, tam yanÄ±ta düÅŸülüyor: %s", e)
            yield self.dusun(sistem_prompt, mesajlar, model=model)

    def _stream_openai_uyumlu(
        self,
        base_url: str,
        api_key: str,
        model: str,
        sistem_prompt: str,
        mesajlar: list[dict],
    ) -> Generator[str, None, None]:
        """OpenAI /v1/chat/completions SSE akÄ±ÅŸÄ±nÄ± yield eder.

        base_url sondaki /v1 varsa temizlenir (config'de /v1 olabilir).
        """
        temiz_url = base_url.rstrip("/")
        if temiz_url.endswith("/v1"):
            temiz_url = temiz_url[:-3]
        url = f"{temiz_url}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": sistem_prompt}] + mesajlar,
            "stream": True,
            "temperature": _VARSAYILAN_SICAKLIK,
            "max_tokens": _VARSAYILAN_MAX_TOKEN,
        }
        with requests.post(
            url, headers=headers, json=payload, stream=True, timeout=TIMEOUT_SANIYE
        ) as r:
            r.raise_for_status()
            for satir in r.iter_lines():
                if not satir:
                    continue
                satir_str = satir.decode("utf-8", errors="replace")
                if not satir_str.startswith("data: "):
                    continue
                veri = satir_str[6:]
                if veri.strip() == "[DONE]":
                    break
                try:
                    parcali = json.loads(veri)
                    delta = parcali["choices"][0].get("delta", {})
                    token = delta.get("content", "")
                    if token:
                        yield token
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue

    def _stream_anthropic(
        self,
        api_key: str,
        model: str,
        sistem_prompt: str,
        mesajlar: list[dict],
    ) -> Generator[str, None, None]:
        """Anthropic Messages API akÄ±ÅŸÄ±nÄ± text_delta olaylarÄ± üzerinden yield eder."""
        ant_base = (
            self.config.get("providers", {})
            .get("anthropic", {})
            .get("base_url", "https://api.anthropic.com")
        )
        url = f"{ant_base}/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        ant_mesajlar = [m for m in mesajlar if m["role"] in ("user", "assistant")]
        payload = {
            "model": model,
            "system": sistem_prompt,
            "messages": ant_mesajlar,
            "max_tokens": _VARSAYILAN_MAX_TOKEN,
            "stream": True,
        }
        with requests.post(
            url, headers=headers, json=payload, stream=True, timeout=TIMEOUT_SANIYE
        ) as r:
            r.raise_for_status()
            for satir in r.iter_lines():
                if not satir:
                    continue
                satir_str = satir.decode("utf-8", errors="replace")
                if not satir_str.startswith("data: "):
                    continue
                try:
                    olay = json.loads(satir_str[6:])
                    if olay.get("type") == "content_block_delta":
                        delta = olay.get("delta", {})
                        if delta.get("type") == "text_delta":
                            yield delta.get("text", "")
                except json.JSONDecodeError:
                    continue

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Provider dispatch
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _cagir(
        self,
        adim: SaglayCiAdim,
        sistem_prompt: str,
        mesajlar: list[dict],
    ) -> LLMYanitMeta:
        """DoÄŸru provider çaÄŸrÄ± metodunu seçer ve LLMYanitMeta döndürür."""
        t0 = time.monotonic()

        dispatch: dict[str, Callable[[], str]] = {
            "lmstudio": lambda: self._cagir_lmstudio(
                adim.base_url, adim.model, sistem_prompt, mesajlar
            ),
            "anthropic": lambda: self._cagir_anthropic(
                adim.base_url, adim.api_key, adim.model, sistem_prompt, mesajlar
            ),
            "moonshot": lambda: self._cagir_moonshot(
                adim.api_key, adim.model, sistem_prompt, mesajlar
            ),
            "azure": lambda: self._cagir_azure(
                adim.api_key, adim.model, sistem_prompt, mesajlar
            ),
            "bedrock": lambda: self._cagir_bedrock(adim.model, sistem_prompt, mesajlar),
            "gemini": lambda: self._cagir_gemini(
                adim.base_url, adim.api_key, adim.model, sistem_prompt, mesajlar
            ),
            "gemini_cloud": lambda: self._cagir_gemini(
                adim.base_url, adim.api_key, adim.model, sistem_prompt, mesajlar
            ),
            "openrouter": lambda: self._cagir_openai_uyumlu(
                adim.base_url, adim.api_key, adim.model, sistem_prompt, mesajlar
            ),
            "lmstudio_reasoning": lambda: self._cagir_lmstudio_reasoning(
                adim.model, sistem_prompt, mesajlar
            ),
            "codex_responses": lambda: self._cagir_codex_responses(
                adim.model, sistem_prompt, mesajlar
            ),
            # â”€â”€ Yeni OpenAI-uyumlu saÄŸlayÄ±cÄ±lar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
            "together": lambda: self._cagir_openai_uyumlu(
                adim.base_url, adim.api_key, adim.model, sistem_prompt, mesajlar
            ),
            "fireworks": lambda: self._cagir_openai_uyumlu(
                adim.base_url, adim.api_key, adim.model, sistem_prompt, mesajlar
            ),
            "mistral": lambda: self._cagir_openai_uyumlu(
                adim.base_url, adim.api_key, adim.model, sistem_prompt, mesajlar
            ),
            "cohere": lambda: self._cagir_openai_uyumlu(
                adim.base_url, adim.api_key, adim.model, sistem_prompt, mesajlar
            ),
            "perplexity": lambda: self._cagir_openai_uyumlu(
                adim.base_url, adim.api_key, adim.model, sistem_prompt, mesajlar
            ),
        }

        # Provider Abstraction entegrasyonu â€” deepseek, openai, xai
        if _PA_AKTIF and adim.provider in ("deepseek", "openai", "xai"):
            pa_provider = get_provider(
                adim.provider,
                model=adim.model,
                api_key=adim.api_key,
                base_url=adim.base_url,
                config=self.config,
            )
            if pa_provider and pa_provider.hazir_mi():
                fn = lambda p=pa_provider, s=sistem_prompt, m=mesajlar: (  # noqa: E731
                    p.chat(m, s).metin
                )
            else:
                fn = dispatch.get(
                    adim.provider,
                    lambda: self._cagir_openai_uyumlu(
                        adim.base_url, adim.api_key, adim.model, sistem_prompt, mesajlar
                    ),
                )
        else:
            fn = dispatch.get(
                adim.provider,
                lambda: self._cagir_openai_uyumlu(
                    adim.base_url, adim.api_key, adim.model, sistem_prompt, mesajlar
                ),
            )
        metin = fn()

        tahmini_token = (
            len(sistem_prompt.split())
            + sum(len(m.get("content", "").split()) for m in mesajlar)
            + len(metin.split())
        )

        return LLMYanitMeta(
            metin=metin,
            provider=adim.provider,
            model=adim.model,
            sure_sn=time.monotonic() - t0,
            tahmini_token=tahmini_token,
        )

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Genel provider çaÄŸrÄ± metodu (harici kullanÄ±m)
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    @trace_llm_call()
    def provider_cagir(
        self,
        provider: str,
        model: str,
        mesajlar: list[dict],
        sistem_prompt: str = "",
    ) -> str:
        """Herhangi bir provider'a API çaÄŸrÄ±sÄ± yap.

        Config'den base_url ve api_key'i okur, doÄŸru API metoduna yönlendirir.
        try/except ile güvenli â€” hata durumunda "[Beyin HatasÄ±] â€¦" döner.

        Args:
            provider:      SaÄŸlayÄ±cÄ± adÄ± (ör. "openai", "anthropic", "gemini").
            model:         Model adÄ±.
            mesajlar:      KonuÅŸma mesajlarÄ± listesi.
            sistem_prompt: Sistem prompt'u (opsiyonel).

        Returns:
            LLM yanÄ±t metni veya "[Beyin HatasÄ±] â€¦" hata dizesi.
        """
        try:
            prov_conf = self.config.get("providers", {}).get(provider, {})
            base_url = prov_conf.get("base_url", self.base_url)
            api_key = self._anahtar_bul(provider, prov_conf)

            adim = SaglayCiAdim(
                provider=provider,
                model=model,
                base_url=base_url,
                api_key=api_key,
            )

            t0 = time.monotonic()

            dispatch: dict[str, Callable[[], str]] = {
                "lmstudio": lambda: self._cagir_lmstudio(
                    adim.base_url, adim.model, sistem_prompt, mesajlar
                ),
                "anthropic": lambda: self._cagir_anthropic(
                    adim.base_url, adim.api_key, adim.model, sistem_prompt, mesajlar
                ),
                "moonshot": lambda: self._cagir_moonshot(
                    adim.api_key, adim.model, sistem_prompt, mesajlar
                ),
                "azure": lambda: self._cagir_azure(
                    adim.api_key, adim.model, sistem_prompt, mesajlar
                ),
                "bedrock": lambda: self._cagir_bedrock(
                    adim.model, sistem_prompt, mesajlar
                ),
                "gemini": lambda: self._cagir_gemini(
                    adim.base_url, adim.api_key, adim.model, sistem_prompt, mesajlar
                ),
                "gemini_cloud": lambda: self._cagir_gemini(
                    adim.base_url, adim.api_key, adim.model, sistem_prompt, mesajlar
                ),
                "openrouter": lambda: self._cagir_openai_uyumlu(
                    adim.base_url, adim.api_key, adim.model, sistem_prompt, mesajlar
                ),
                "openai": lambda: self._cagir_openai_uyumlu(
                    adim.base_url, adim.api_key, adim.model, sistem_prompt, mesajlar
                ),
                # â”€â”€ Yeni OpenAI-uyumlu saÄŸlayÄ±cÄ±lar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
                "together": lambda: self._cagir_openai_uyumlu(
                    adim.base_url, adim.api_key, adim.model, sistem_prompt, mesajlar
                ),
                "fireworks": lambda: self._cagir_openai_uyumlu(
                    adim.base_url, adim.api_key, adim.model, sistem_prompt, mesajlar
                ),
                "mistral": lambda: self._cagir_openai_uyumlu(
                    adim.base_url, adim.api_key, adim.model, sistem_prompt, mesajlar
                ),
                "cohere": lambda: self._cagir_openai_uyumlu(
                    adim.base_url, adim.api_key, adim.model, sistem_prompt, mesajlar
                ),
                "perplexity": lambda: self._cagir_openai_uyumlu(
                    adim.base_url, adim.api_key, adim.model, sistem_prompt, mesajlar
                ),
            }

            # Provider Abstraction entegrasyonu â€” deepseek, openai, xai
            if _PA_AKTIF and adim.provider in ("deepseek", "openai", "xai"):
                pa_provider = get_provider(
                    adim.provider,
                    model=adim.model,
                    api_key=adim.api_key,
                    base_url=adim.base_url,
                    config=self.config,
                )
                if pa_provider and pa_provider.hazir_mi():
                    fn = lambda p=pa_provider, s=sistem_prompt, m=mesajlar: (  # noqa: E731
                        p.chat(m, s).metin
                    )
                else:
                    fn = dispatch.get(
                        adim.provider,
                        lambda: self._cagir_openai_uyumlu(
                            adim.base_url,
                            adim.api_key,
                            adim.model,
                            sistem_prompt,
                            mesajlar,
                        ),
                    )
            else:
                fn = dispatch.get(
                    adim.provider,
                    lambda: self._cagir_openai_uyumlu(
                        adim.base_url,
                        adim.api_key,
                        adim.model,
                        sistem_prompt,
                        mesajlar,
                    ),
                )
            metin = fn()
            sure = time.monotonic() - t0
            logger.info(
                "[Beyin] provider_cagir(%s, %s) = %.1fs",
                provider,
                model,
                sure,
            )
            return metin

        except Exception as e:
            logger.error(
                "[Beyin] provider_cagir(%s, %s) hatasi: %s",
                provider,
                model,
                e,
            )
            return f"[Beyin HatasÄ±] {provider}/{model}: {e}"

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Provider implementasyonlarÄ±
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _cagir_lmstudio(
        self,
        base_url: str,
        model: str,
        sistem_prompt: str,
        mesajlar: list[dict],
    ) -> str:
        """LM Studio: sistem mesajÄ± [SISTEM]: öneki ile user rolüne çevrilir."""
        url = f"{base_url}/v1/chat/completions"
        donusturulmus: list[dict] = []
        if sistem_prompt:
            donusturulmus.append(
                {"role": "user", "content": f"[SISTEM]: {sistem_prompt}"}
            )
        for m in mesajlar:
            if m["role"] == "system":
                donusturulmus.append(
                    {"role": "user", "content": f"[SISTEM]: {m['content']}"}
                )
            else:
                donusturulmus.append(m)

        payload = {
            "model": model,
            "messages": donusturulmus,
            "stream": False,
            "temperature": _VARSAYILAN_SICAKLIK,
            "max_tokens": _VARSAYILAN_MAX_TOKEN,
        }
        r = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=TIMEOUT_SANIYE,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def _cagir_openai_uyumlu(
        self,
        base_url: str,
        api_key: str,
        model: str,
        sistem_prompt: str,
        mesajlar: list[dict],
    ) -> str:
        """Genel OpenAI-uyumlu /v1/chat/completions çaÄŸrÄ±sÄ±.

        base_url sondaki /v1 varsa temizlenir (config'de /v1 olabilir).
        """
        # Sondaki /v1 varsa temizle, kod sabit /v1/chat/completions ekler
        temiz_url = base_url.rstrip("/")
        if temiz_url.endswith("/v1"):
            temiz_url = temiz_url[:-3]
        url = f"{temiz_url}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": sistem_prompt}] + mesajlar,
            "stream": False,
            "temperature": _VARSAYILAN_SICAKLIK,
            "max_tokens": _VARSAYILAN_MAX_TOKEN,
        }
        r = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT_SANIYE)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def _cagir_anthropic(
        self,
        base_url: str,
        api_key: str,
        model: str,
        sistem_prompt: str,
        mesajlar: list[dict],
    ) -> str:
        """Anthropic /v1/messages çaÄŸrÄ±sÄ±."""
        url = f"{base_url}/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        ant_mesajlar = [m for m in mesajlar if m["role"] in ("user", "assistant")]
        payload = {
            "model": model,
            "system": sistem_prompt,
            "messages": ant_mesajlar,
            "max_tokens": _VARSAYILAN_MAX_TOKEN,
        }
        r = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT_SANIYE)
        r.raise_for_status()
        return r.json()["content"][0]["text"]

    def _cagir_moonshot(
        self,
        api_key: str,
        model: str,
        sistem_prompt: str,
        mesajlar: list[dict],
    ) -> str:
        """Moonshot AI çaÄŸrÄ±sÄ±; moonshot_schema tercih edilir, yoksa REST."""
        try:
            from reymen.sistem.moonshot_schema import MoonshotProvider  # type: ignore[import]

            mp = MoonshotProvider(model=model, api_key=api_key)
            return mp.uret(sistem_prompt, mesajlar)
        except ImportError:
            url = os.environ.get("MOONSHOT_BASE_URL", "https://api.moonshot.cn/v1")
            return self._cagir_openai_uyumlu(
                url, api_key, model, sistem_prompt, mesajlar
            )

    def _cagir_azure(
        self,
        api_key: str,
        model: str,
        sistem_prompt: str,
        mesajlar: list[dict],
    ) -> str:
        """Azure OpenAI çaÄŸrÄ±sÄ±."""
        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
        version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01")
        if not endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT ortam deÄŸiÅŸkeni ayarlÄ± deÄŸil")

        url = f"{endpoint}/openai/deployments/{model}/chat/completions?api-version={version}"
        headers = {"api-key": api_key, "Content-Type": "application/json"}
        payload = {
            "messages": [{"role": "system", "content": sistem_prompt}] + mesajlar,
            "temperature": _VARSAYILAN_SICAKLIK,
            "max_tokens": _VARSAYILAN_MAX_TOKEN,
        }
        r = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT_SANIYE)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def _cagir_bedrock(
        self,
        model: str,
        sistem_prompt: str,
        mesajlar: list[dict],
    ) -> str:
        """AWS Bedrock çaÄŸrÄ±sÄ±; bedrock_adapter gerektirir."""
        try:
            from reymen.sistem.bedrock_adapter import BedrockAdapter  # type: ignore[import]
        except ImportError as exc:
            raise RuntimeError("bedrock_adapter modülü bulunamadÄ±") from exc

        adapter = BedrockAdapter(
            region=os.environ.get("AWS_REGION", "us-east-1"),
        )
        return adapter.uret(sistem_prompt, mesajlar)

    def _cagir_gemini(
        self,
        base_url: str,
        api_key: str,
        model: str,
        sistem_prompt: str,
        mesajlar: list[dict],
    ) -> str:
        """Google Gemini REST API (generateContent) çaÄŸrÄ±sÄ±.

        Config'den gelen base_url (https://generativelanguage.googleapis.com)
        ve api_key (GEMINI_API_KEY) ile çalÄ±ÅŸÄ±r.
        Fallback: Vertex AI adapter (gemini_cloudcode_adapter).
        """
        # 1. Vertex AI / Cloud Code adapter (opsiyonel)
        try:
            from reymen.sistem.gemini_cloudcode_adapter import GeminiCloudCodeAdapter  # type: ignore[import]

            adapter = GeminiCloudCodeAdapter(
                project=os.environ.get("GOOGLE_CLOUD_PROJECT", ""),
                location=os.environ.get("VERTEX_AI_LOCATION", "us-central1"),
                model=model,
            )
            return adapter.uret(sistem_prompt, mesajlar)
        except ImportError as _e:
            logger.warning("[Beyin] Modul yuklenemedi (L1122): %s", ImportError)
            pass

        # 2. REST API key tabanlÄ± (Google AI Studio)
        temiz_url = base_url.rstrip("/")
        url = f"{temiz_url}/models/{model}:generateContent"

        headers = {"Content-Type": "application/json"}
        # Gemini API key URL parametresi olarak gider
        params = {"key": api_key}

        # Gemini mesaj formatÄ±: contents[{role, parts[{text}]}]
        gemini_icerkler: list[dict] = []
        if sistem_prompt:
            gemini_icerkler.append(
                {
                    "role": "user",
                    "parts": [{"text": f"[SISTEM] {sistem_prompt}"}],
                }
            )
        for m in mesajlar:
            rol = m.get("role", "user")
            icerik = m.get("content", "")
            # Gemini roles: user, model (not assistant)
            gemini_rol = "model" if rol in ("assistant", "model") else "user"
            gemini_icerkler.append(
                {
                    "role": gemini_rol,
                    "parts": [{"text": icerik}],
                }
            )

        payload = {
            "contents": gemini_icerkler,
            "generationConfig": {
                "temperature": _VARSAYILAN_SICAKLIK,
                "maxOutputTokens": _VARSAYILAN_MAX_TOKEN,
            },
        }

        r = requests.post(
            url,
            headers=headers,
            params=params,
            json=payload,
            timeout=TIMEOUT_SANIYE,
        )
        r.raise_for_status()
        veri = r.json()
        # YanÄ±t: candidates[0].content.parts[0].text
        try:
            return veri["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as exc:
            raise RuntimeError(
                f"Gemini beklenmeyen yanÄ±t formatÄ±: {json.dumps(veri, ensure_ascii=False)[:500]}"
            ) from exc

    def _cagir_lmstudio_reasoning(
        self,
        model: str,
        sistem_prompt: str,
        mesajlar: list[dict],
    ) -> str:
        """LM Studio derin akÄ±l yürütme modu; yoksa standart LM Studio'ya düÅŸer."""
        try:
            from reymen.sistem.lmstudio_reasoning import LMStudioReasoning  # type: ignore[import]

            lm = LMStudioReasoning(base_url=self.base_url)
            tam_prompt = f"{sistem_prompt}\n\n" + "\n".join(
                f"{m['role'].upper()}: {m['content']}" for m in mesajlar
            )
            sonuc = lm.dusun(tam_prompt, derinlik="derin")
            if sonuc.get("basarili"):
                return sonuc["yanit"]
            raise RuntimeError(sonuc.get("hata", "LMStudio reasoning hatasÄ±"))
        except ImportError:
            return self._cagir_lmstudio(self.base_url, model, sistem_prompt, mesajlar)

    def _cagir_codex_responses(
        self,
        model: str,
        sistem_prompt: str,
        mesajlar: list[dict],
    ) -> str:
        """OpenAI Codex Responses API; codex_responses_adapter gerektirir."""
        try:
            from reymen.cereyan.codex_responses_adapter import CodexResponsesAdapter  # type: ignore[import]
        except ImportError as exc:
            raise RuntimeError("codex_responses_adapter modülü bulunamadÄ±") from exc

        adapter = CodexResponsesAdapter(model=model)
        return adapter.uret(sistem_prompt, mesajlar)

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # YardÄ±mcÄ±: kullanÄ±m kaydÄ±
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _kullanim_kaydet(
        self,
        adim: SaglayCiAdim,
        sistem_prompt: str,
        mesajlar: list[dict],
        yanit: str,
    ) -> None:
        """account_usage ile kullanÄ±m kaydÄ± oluÅŸturur; sessizce baÅŸarÄ±sÄ±z olur."""
        try:
            from reymen.sistem.account_usage import AccountUsage  # type: ignore[import]
            from reymen.sistem.budget_config import BudgetConfig  # type: ignore[import]

            _au = AccountUsage()
            girdi_token = (len(sistem_prompt) + sum(len(str(m)) for m in mesajlar)) // 4
            cikti_token = len(yanit) // 4
            toplam = girdi_token + cikti_token
            _bc = BudgetConfig()
            try:
                maliyet = _bc.provider_maliyeti(adim.provider, toplam)
            except Exception:
                maliyet = toplam
            try:
                _au.ekle(adim.provider, adim.model, girdi_token, cikti_token, maliyet)
            except Exception as _e2:
                logger.debug("[Beyin] _kullanim_kaydet maliyet: %s", _e2)
                _au.ekle(adim.provider, adim.model, girdi_token, cikti_token, toplam)
        except Exception as _e:
            logger.debug("[Beyin] _kullanim_kaydet: %s", _e)
            pass

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Yönlendirici & eriÅŸilebilirlik yardÄ±mcÄ±larÄ±
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def rota_belirle(self, hedef: str) -> Tuple[str, str]:
        """AkÄ±llÄ± yönlendirici ile göreve göre en iyi (provider, model) seç.

        Returns:
            (provider_adÄ±, model_adÄ±) â€” router yoksa varsayÄ±lanÄ± döner.
        """
        try:
            from reymen.cereyan.akilli_yonlendirici import (  # type: ignore[import]
                gorev_icin_model_sec,
                musait_providerlar_bul,
            )

            musait = musait_providerlar_bul(self.config)
            if musait:
                prov, mdl = gorev_icin_model_sec(hedef, musait)
                if prov != self.provider or mdl != self.model:
                    logger.info("[Router] %s/%s seçildi.", prov, mdl)
                return prov, mdl
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")
        return self.provider, self.model

    def ping(self, provider: Optional[str] = None) -> bool:
        """SaÄŸlayÄ±cÄ± eriÅŸilebilirliÄŸini basit bir HTTP isteÄŸiyle kontrol eder.

        Args:
            provider: Kontrol edilecek saÄŸlayÄ±cÄ±; None ise birincil saÄŸlayÄ±cÄ±.

        Returns:
            True â€” saÄŸlayÄ±cÄ± eriÅŸilebilir; False â€” deÄŸil.
        """
        pname = provider or self.provider
        pconf = self.config.get("providers", {}).get(pname, {})
        url_kok = pconf.get("base_url", self.base_url)

        try:
            if pname in ("lmstudio", "ollama"):
                r = requests.get(f"{url_kok}/v1/models", timeout=5)
                return r.status_code == 200

            key = self._anahtar_bul(pname, pconf)
            r = requests.get(
                f"{url_kok}/v1/models",
                headers={"Authorization": f"Bearer {key}"},
                timeout=5,
            )
            return r.status_code < 500
        except Exception:
            return False

    def aktif_providerlar(self) -> List[str]:
        """Ping testi geçen saÄŸlayÄ±cÄ±larÄ±n listesini döndürür."""
        return [a.provider for a in self._fallback_zinciri if self.ping(a.provider)]


# â”€â”€ HÄ±zlÄ± test â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    cfg: dict[str, Any] = {
        "default_provider": "lmstudio",
        "default_model": "cognitivecomputations.dolphin3.0-llama3.1-8b",
        "providers": {
            "lmstudio": {"base_url": "http://localhost:1234", "api_key": "not-needed"},
            "deepseek": {"base_url": "https://api.deepseek.com", "api_key": ""},
        },
        "fallback_model": None,
    }

    b = Beyin(cfg)
    print("Fallback zinciri:", b._fallback_zinciri)
    print("LM Studio ping:", b.ping("lmstudio"))
