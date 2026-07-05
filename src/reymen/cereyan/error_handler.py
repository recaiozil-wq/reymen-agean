# -*- coding: utf-8 -*-
"""API error classification — akilli failover ve kurtarma.

Hermes agent/error_classifier.py + turn_retry_state.py'den adapte.
ReYMeN'e ozgu: deepseek/openrouter/xiaomi/groq provider'lari.
Hermes bagimliligi YOK.
"""
from __future__ import annotations

import enum
import logging
from dataclasses import dataclass, fields
from typing import Any, Optional

logger = logging.getLogger("conversation_loop")


# ── Hata taksonomisi ────────────────────────────────────────────────

class FailoverReason(enum.Enum):
    """API hatasinin sebebi — kurtarma stratejisini belirler."""

    auth = "auth"                       # 401/403 — gecici, refresh dene
    auth_permanent = "auth_permanent"   # Refresh sonrasi da basarisiz — dur
    billing = "billing"                 # 402/bakiye bitti — provider degistir
    rate_limit = "rate_limit"           # 429 — bekle, sonra fallback
    overloaded = "overloaded"           # 503/529 — bekle, tekrar dene
    server_error = "server_error"       # 500/502 — tekrar dene
    timeout = "timeout"                 # Zaman asimi — client yenile + retry
    context_overflow = "context_overflow"  # Context cok buyuk — sikistir
    payload_too_large = "payload_too_large"  # 413 — payload kucult
    model_not_found = "model_not_found"  # Model bulunamadi — farkli model dene
    content_policy_blocked = "content_policy_blocked"  # Guvenlik filtresi
    format_error = "format_error"       # 400 — istek formati bozuk
    unknown = "unknown"                 # Siniflandirilamayan — retry


# ── Siniflandirma sonucu ────────────────────────────────────────────

@dataclass
class SiniflandirilmisHata:
    """API hatasinin yapisal siniflandirmasi."""

    reason: FailoverReason
    status_code: Optional[int] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    message: str = ""
    retryable: bool = True
    should_rotate: bool = False
    should_fallback: bool = False
    should_compress: bool = False
    error_context: Optional[dict] = None

    @property
    def is_auth(self) -> bool:
        return self.reason in (FailoverReason.auth, FailoverReason.auth_permanent)


# ── Provider-specific patterns ──────────────────────────────────────

_BILLING_PATTERNS = [
    "insufficient", "bakiye", "quota", "402", "credit",
    "payment", "billing", "exceeded",
]

_RATE_LIMIT_PATTERNS = [
    "429", "rate limit", "too many requests", "ratelimit",
]

_AUTH_PATTERNS = [
    "401", "403", "unauthorized", "forbidden", "invalid api key",
    "authentication", "auth", "permission denied",
]

_TIMEOUT_PATTERNS = [
    "timeout", "timed out", "connection refused", "connection error",
    "deadline exceeded",
]

_OVERLOAD_PATTERNS = [
    "503", "529", "overloaded", "service unavailable", "too many",
]

_CONTEXT_PATTERNS = [
    "context length", "context window", "too long", "max tokens",
    "token limit", "maximum length",
]


# ── Ana siniflandirici ──────────────────────────────────────────────

def api_hatasini_siniflandir(
    hata_metni: str,
    status_code: Optional[int] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> SiniflandirilmisHata:
    """API hatasini siniflandir ve kurtarma aksiyonu belirle.

    Args:
        hata_metni: Hata mesaji (string).
        status_code: HTTP status code (varsa).
        provider: Provider adi.
        model: Model adi.

    Returns:
        SiniflandirilmisHata nesnesi.
    """
    hata_lower = (hata_metni or "").lower()
    ctx = {"status_code": status_code, "provider": provider, "model": model}

    # 1. Bakiye
    if any(p in hata_lower for p in _BILLING_PATTERNS) or status_code == 402:
        return SiniflandirilmisHata(
            reason=FailoverReason.billing, status_code=status_code,
            provider=provider, model=model, message=hata_metni,
            retryable=True, should_rotate=True, should_fallback=True,
            error_context=ctx,
        )

    # 2. Auth
    if any(p in hata_lower for p in _AUTH_PATTERNS) or status_code in (401, 403):
        return SiniflandirilmisHata(
            reason=FailoverReason.auth, status_code=status_code,
            provider=provider, model=model, message=hata_metni,
            retryable=True, should_rotate=True, should_fallback=True,
            error_context=ctx,
        )

    # 3. Rate limit
    if any(p in hata_lower for p in _RATE_LIMIT_PATTERNS) or status_code == 429:
        return SiniflandirilmisHata(
            reason=FailoverReason.rate_limit, status_code=status_code,
            provider=provider, model=model, message=hata_metni,
            retryable=True, should_rotate=False, should_fallback=True,
            error_context=ctx,
        )

    # 4. Context overflow
    if any(p in hata_lower for p in _CONTEXT_PATTERNS):
        return SiniflandirilmisHata(
            reason=FailoverReason.context_overflow, status_code=status_code,
            provider=provider, model=model, message=hata_metni,
            retryable=True, should_rotate=False, should_fallback=False,
            should_compress=True, error_context=ctx,
        )

    # 5. Overloaded
    if any(p in hata_lower for p in _OVERLOAD_PATTERNS) or status_code in (503, 529):
        return SiniflandirilmisHata(
            reason=FailoverReason.overloaded, status_code=status_code,
            provider=provider, model=model, message=hata_metni,
            retryable=True, should_rotate=False, should_fallback=True,
            error_context=ctx,
        )

    # 6. Timeout
    if any(p in hata_lower for p in _TIMEOUT_PATTERNS):
        return SiniflandirilmisHata(
            reason=FailoverReason.timeout, status_code=status_code,
            provider=provider, model=model, message=hata_metni,
            retryable=True, should_rotate=False, should_fallback=True,
            error_context=ctx,
        )

    # 7. Server error
    if status_code and 500 <= status_code < 600:
        return SiniflandirilmisHata(
            reason=FailoverReason.server_error, status_code=status_code,
            provider=provider, model=model, message=hata_metni,
            retryable=True, should_rotate=False, should_fallback=True,
            error_context=ctx,
        )

    # 8. Format error
    if status_code == 400:
        return SiniflandirilmisHata(
            reason=FailoverReason.format_error, status_code=status_code,
            provider=provider, model=model, message=hata_metni,
            retryable=False, should_rotate=False, should_fallback=False,
            error_context=ctx,
        )

    # 9. Unknown
    return SiniflandirilmisHata(
        reason=FailoverReason.unknown, status_code=status_code,
        provider=provider, model=model, message=hata_metni,
        retryable=True, should_rotate=False, should_fallback=True,
        error_context=ctx,
    )


# Geriye uyumlu alias
classify_api_error = api_hatasini_siniflandir


# ── TurnRetryState (Hermes turn_retry_state.py'den adapte) ──────────

@dataclass
class TurnRetryState:
    """Tek API cagrisi icin kurtarma guard'lari + restart sinyalleri.

    Her dis turn (api_call_count) icin yeni bir instance.
    """

    deepseek_auth_retry_attempted: bool = False
    openrouter_auth_retry_attempted: bool = False
    xiaomi_auth_retry_attempted: bool = False
    groq_auth_retry_attempted: bool = False
    image_shrink_retry_attempted: bool = False
    has_retried_429: bool = False
    restart_with_compressed_messages: bool = False
    restart_with_length_continuation: bool = False

    def __iter__(self):
        for f in fields(self):
            yield f.name, getattr(self, f.name)
