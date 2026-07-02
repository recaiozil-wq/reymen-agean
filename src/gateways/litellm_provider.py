# -*- coding: utf-8 -*-
"""
litellm_provider.py — LiteLLM ile 100+ provider entegrasyonu.

LiteLLM, OpenAI formatinda tum saglayicilari tek API'de birlestirir.
Bu modul, ReYMeN'in mevcut provider sistemine LiteLLM'i ekler.

Kullanim:
    from reymen.ag.litellm_provider import litellm_calisitir, litellm_modelleri_listele
    yanit = litellm_calisitir("deepseek/deepseek-v4-flash", "Merhaba")
    modeller = litellm_modelleri_listele("openai")
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# LiteLLM'i opsiyonel yukle
try:
    import litellm
    from litellm import completion, ModelResponse
    _LITELLM_MEVCUT = True
    # Rate limit ve retry ayarlari
    litellm.max_budget = 100.0  # $100 maks butce
    litellm.set_verbose = False
    # Hata durumunda otomatik retry
    litellm.num_retries = 2
    litellm.request_timeout = 60
except ImportError:
    _LITELLM_MEVCUT = False
    completion = None
    ModelResponse = None


# ── Desteklenen Provider'lar ──────────────────────────────────────────────────

# LiteLLM ile kullanilabilir populer provider'lar
# Tam liste: https://docs.litellm.ai/docs/providers
POPULER_PROVIDERLER = {
    # OpenAI uyumlu
    "openai": {"modeller": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "o1", "o3-mini"], "api_key_env": "OPENAI_API_KEY"},
    "azure": {"modeller": ["gpt-4o", "gpt-4"], "api_key_env": "AZURE_API_KEY"},
    
    # Anthropic
    "anthropic": {"modeller": ["claude-sonnet-4", "claude-haiku-4-5", "claude-opus-4"], "api_key_env": "ANTHROPIC_API_KEY"},
    
    # Google
    "gemini": {"modeller": ["gemini-2.5-pro", "gemini-2.0-flash"], "api_key_env": "GEMINI_API_KEY"},
    "vertex_ai": {"modeller": ["gemini-2.5-pro"], "api_key_env": "VERTEX_AI_CREDENTIALS"},
    
    # Meta / Open
    "together": {"modeller": ["llama-3.1-405b", "llama-3.1-70b", "deepseek-v4"], "api_key_env": "TOGETHER_API_KEY"},
    "fireworks": {"modeller": ["llama-3.1-405b", "deepseek-v4"], "api_key_env": "FIREWORKS_API_KEY"},
    "replicate": {"modeller": ["llama-3.1-405b", "llama-3.1-70b"], "api_key_env": "REPLICATE_API_KEY"},
    
    # DeepSeek
    "deepseek": {"modeller": ["deepseek-v4-flash", "deepseek-v4", "deepseek-r1"], "api_key_env": "DEEPSEEK_API_KEY"},
    
    # Groq (hizli inference)
    "groq": {"modeller": ["llama-3.1-70b", "llama-3.1-8b", "mixtral-8x7b"], "api_key_env": "GROQ_API_KEY"},
    
    # Amazon
    "bedrock": {"modeller": ["claude-sonnet-4", "claude-haiku"], "api_key_env": "AWS_ACCESS_KEY_ID"},
    "sagemaker": {"modeller": ["custom"], "api_key_env": "AWS_ACCESS_KEY_ID"},
    
    # diger
    "perplexity": {"modeller": ["sonar-pro", "sonar"], "api_key_env": "PERPLEXITY_API_KEY"},
    "cohere": {"modeller": ["command-r-plus", "command-r"], "api_key_env": "COHERE_API_KEY"},
    "mistral": {"modeller": ["mistral-large", "mistral-medium"], "api_key_env": "MISTRAL_API_KEY"},
    "xai": {"modeller": ["grok-2", "grok-2-latest"], "api_key_env": "XAI_API_KEY"},
    "openrouter": {"modeller": ["*"], "api_key_env": "OPENROUTER_API_KEY"},
    "ollama": {"modeller": ["*"], "api_key_env": ""},
    "lmstudio": {"modeller": ["*"], "api_key_env": ""},
}

# Mevcut .env'den API key'leri oku
def _env_anahtar(env_adi: str) -> Optional[str]:
    """Environment variable'dan API anahtari oku."""
    if not env_adi:
        return None
    val = os.getenv(env_adi)
    if val:
        return val
    # .env dosyasindan oku
    env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith(env_adi + "="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def aktif_providerlar() -> List[Dict[str, Any]]:
    """API key'i olan provider'lari listele.

    Returns:
        API key'i tanimli provider listesi
    """
    aktif = []
    for ad, bilgi in POPULER_PROVIDERLER.items():
        api_key = _env_anahtar(bilgi["api_key_env"])
        if api_key or not bilgi["api_key_env"]:  # API key gerektirmeyenler (ollama, lmstudio)
            aktif.append({
                "ad": ad,
                "modeller": bilgi["modeller"],
                "api_key_var": bool(api_key),
                "api_key_env": bilgi["api_key_env"],
            })
    return aktif


def litellm_calisitir(
    model: str,
    mesajlar: List[Dict[str, str]],
    **kwargs
) -> Optional[Dict[str, Any]]:
    """LiteLLM ile model cagrisi yap.

    Args:
        model: Model adi (orn: "deepseek/deepseek-v4-flash", "openai/gpt-4o")
        mesajlar: [{"role": "user", "content": "..."}]
        **kwargs: Ek parametreler (temperature, max_tokens, vb.)

    Returns:
        Yanit dict veya None
    """
    if not _LITELLM_MEVCUT:
        logger.error("LiteLLM kurulu degil. pip install litellm")
        return None

    try:
        response = completion(
            model=model,
            messages=mesajlar,
            **kwargs
        )
        if response is None:
            return None
        
        return {
            "icerik": response.choices[0].message.content if response.choices else "",
            "model": response.model if hasattr(response, "model") else model,
            "tokens": {
                "giris": response.usage.prompt_tokens if response.usage else 0,
                "cikis": response.usage.completion_tokens if response.usage else 0,
                "toplam": response.usage.total_tokens if response.usage else 0,
            },
            "sure_sn": response._response_ms / 1000 if hasattr(response, "_response_ms") else 0,
        }
    except Exception as e:
        logger.error("LiteLLM hatasi (%s): %s", model, e)
        return None


def litellm_modelleri_listele(provider: Optional[str] = None) -> List[str]:
    """Kullanilabilir modelleri listele.

    Args:
        provider: Provider filtresi (None = tumu)

    Returns:
        Model adlari listesi
    """
    modeller = []
    for ad, bilgi in POPULER_PROVIDERLER.items():
        if provider and ad != provider:
            continue
        api_key = _env_anahtar(bilgi["api_key_env"])
        if api_key or not bilgi["api_key_env"]:
            for m in bilgi["modeller"]:
                if m == "*":
                    modeller.append(f"{ad}/*")
                else:
                    modeller.append(f"{ad}/{m}")
    return sorted(modeller)


def litellm_durum() -> Dict[str, Any]:
    """LiteLLM durum raporu."""
    aktif = aktif_providerlar()
    toplam_provider = len(POPULER_PROVIDERLER)
    api_keyli = sum(1 for a in aktif if a["api_key_var"])
    
    return {
        "litellm_kurulu": _LITELLM_MEVCUT,
        "toplam_provider": toplam_provider,
        "api_keyli_provider": api_keyli,
        "aktif_provider_sayisi": len(aktif),
        "aktif_providerlar": [a["ad"] for a in aktif],
        "ornek_modeller": litellm_modelleri_listele()[:10],
    }
