# -*- coding: utf-8 -*-
"""Usage/pricing — token tuketimi ve maliyet hesaplama.

ReYMeN'e ozgu, Hermes bagimliligi YOK.
"""
from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger("conversation_loop")

# Provider biri maliyet (USD / 1M token)
# Kaynak: https://api.deepseek.com, https://openrouter.ai, https://console.groq.com
PROVIDER_PRICES = {
    "deepseek": {"input": 0.27, "output": 1.10},
    "deepseek-v4-flash": {"input": 0.27, "output": 1.10},
    "xiaomi": {"input": 0.000036, "output": 0.000036},
    "mimo": {"input": 0.000036, "output": 0.000036},
    "openrouter": {"input": 0.50, "output": 1.50},
    "groq": {"input": 0.10, "output": 0.40},
    "xai": {"input": 0.30, "output": 0.60},
    "anthropic": {"input": 3.00, "output": 15.00},
    "claude": {"input": 3.00, "output": 15.00},
    "gpt4": {"input": 10.00, "output": 30.00},
    "gpt4o": {"input": 2.50, "output": 10.00},
    "lmstudio": {"input": 0.0, "output": 0.0},
    "local": {"input": 0.0, "output": 0.0},
}

PRICE_VARSAYILAN = {"input": 0.50, "output": 1.50}


def normalize_usage(provider_usage: dict) -> dict:
    """Provider'dan gelen kullanim verisini normalize et.

    Args:
        provider_usage: Ham provider kullanim dict'i.

    Returns:
        {"input_tokens": int, "output_tokens": int, "total_tokens": int}
    """
    return {
        "input_tokens": provider_usage.get("prompt_tokens", 0)
        or provider_usage.get("input_tokens", 0)
        or 0,
        "output_tokens": provider_usage.get("completion_tokens", 0)
        or provider_usage.get("output_tokens", 0)
        or 0,
        "total_tokens": provider_usage.get("total_tokens", 0)
        or 0,
    }


def estimate_usage_cost(
    input_tokens: int,
    output_tokens: int,
    provider: Optional[str] = None,
) -> float:
    """Token tuketimine gore maliyet hesapla.

    Args:
        input_tokens: Girdi token sayisi.
        output_tokens: Cikti token sayisi.
        provider: Provider adi (fiyatlandirma icin).

    Returns:
        Tahmini maliyet (USD).
    """
    prices = PRICE_VARSAYILAN
    if provider:
        lower_provider = provider.lower()
        for anahtar, p in PROVIDER_PRICES.items():
            if anahtar in lower_provider:
                prices = p
                break

    input_cost = (input_tokens / 1_000_000) * prices["input"]
    output_cost = (output_tokens / 1_000_000) * prices["output"]
    total = input_cost + output_cost

    if total > 0 and total < 0.0001:
        return 0.0001  # minimum
    return round(total, 6)
