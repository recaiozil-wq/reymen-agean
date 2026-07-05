# -*- coding: utf-8 -*-
"""
observability.py â€” OpenTelemetry LLM observability katmanÄ±.

LLM Ã§aÄŸrÄ±larÄ±, araÃ§ Ã§alÄ±ÅŸtÄ±rmalarÄ±, skill yÃ¼klemeleri ve oturum baÅŸlatmalarÄ±
iÃ§in span'ler oluÅŸturur. config.yaml'deki ``observability`` bÃ¶lÃ¼mÃ¼yle
aÃ§Ä±lÄ±p kapanabilir.

Desteklenen exporter'lar:
    - console  (standart Ã§Ä±ktÄ±ya yazdÄ±rÄ±r, geliÅŸtirme iÃ§in)
    - otlp     (Langfuse/Jaeger gibi OTLP alÄ±cÄ±lara gÃ¶nderir)

KullanÄ±m:
    from reymen.core.observability import (
        setup_observability,
        trace_llm_call,
        trace_tool_call,
        tracer,
        observability_durum,
    )

    # Uygulama baÅŸlangÄ±cÄ±nda bir kez Ã§aÄŸÄ±r (config dict ile veya env vars)
    setup_observability(config={"observability": {"enabled": True, "exporter": "console"}})

    # DekoratÃ¶r olarak
    @trace_llm_call()
    def dusun(self, ...):
        ...

    @trace_tool_call()
    def calistir(self, arac, ham_param):
        ...
"""

from __future__ import annotations

import functools
import logging
import os
import time
import traceback
from contextlib import nullcontext
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

# â”€â”€ Global durum â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_TRACER = None
_TRACER_PROVIDER = None
_OBSERVABILITY_AKTIF = False


# â”€â”€ Config okuyucu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def _config_oku(config: Optional[dict]) -> dict:
    """config.yaml'deki observability bÃ¶lÃ¼mÃ¼nÃ¼ okur; yoksa varsayÄ±lan dÃ¶ndÃ¼rÃ¼r."""
    if config is None:
        config = {}
    obs = config.get("observability", {}) if isinstance(config, dict) else {}
    return {
        "enabled": bool(obs.get("enabled", False)),
        "exporter": str(obs.get("exporter", "console")),
        "endpoint": str(obs.get("endpoint", "")),
        "service_name": str(config.get("agent", {}).get("name", "reymen-agent"))
        if isinstance(config, dict)
        else "reymen-agent",
        "service_version": "1.0.0",
    }


# â”€â”€ Langfuse env vars (geriye uyumluluk) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
LANGFUSE_PUBLIC_KEY = os.environ.get("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY = os.environ.get("LANGFUSE_SECRET_KEY", "")

LANGFUSE_OTLP_TRACES_ENDPOINT = os.environ.get(
    "LANGFUSE_OTLP_TRACES_ENDPOINT",
    "https://cloud.langfuse.com/api/public/otlp/v1/traces",
)


def _langfuse_kimlik_bilgisi_var() -> bool:
    """Langfuse kimlik bilgileri ortamda mevcut mu?"""
    return bool(LANGFUSE_PUBLIC_KEY) and bool(LANGFUSE_SECRET_KEY)


# â”€â”€ Public API â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def setup_observability(
    config: Optional[dict] = None,
    service_name: str = "reymen-agent",
    service_version: str = "1.0.0",
) -> bool:
    """OpenTelemetry tracer'Ä± baÅŸlat veya kapat.

    Ã–ncelik sÄ±rasÄ±:
        1. ``config`` dict iÃ§indeki ``observability`` bÃ¶lÃ¼mÃ¼ (birincil)
        2. LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY env var'larÄ± (geriye uyumlu)
        3. HiÃ§biri yoksa â†’ no-op tracer (hiÃ§bir span gÃ¶nderilmez)

    Args:
        config:         config.yaml dict (observability.enabled/exporter/endpoint).
        service_name:   OpenTelemetry servis adÄ± (config yoksa kullanÄ±lÄ±r).
        service_version: OpenTelemetry servis versiyonu.

    Returns:
        True ise observability aktif, False ise devre dÄ±ÅŸÄ±.
    """
    global _TRACER, _TRACER_PROVIDER, _OBSERVABILITY_AKTIF

    if _TRACER is not None:
        return _OBSERVABILITY_AKTIF  # Zaten baÅŸlatÄ±lmÄ±ÅŸ

    # 1. Config'den oku
    obs_conf = _config_oku(config)

    if obs_conf["enabled"]:
        exporter = obs_conf["exporter"]
        if exporter == "otlp":
            # OTLP exporter â€” endpoint gerekli
            endpoint = obs_conf["endpoint"] or LANGFUSE_OTLP_TRACES_ENDPOINT
            if _langfuse_kimlik_bilgisi_var():
                success = _setup_langfuse_tracer(
                    obs_conf["service_name"],
                    obs_conf["service_version"],
                )
            else:
                success = _setup_otlp_tracer(
                    obs_conf["service_name"],
                    obs_conf["service_version"],
                    endpoint,
                )
            if success:
                _OBSERVABILITY_AKTIF = True
                return True

        # 2. Console exporter (varsayÄ±lan)
        try:
            _setup_console_tracer(
                obs_conf["service_name"],
                obs_conf["service_version"],
            )
            _OBSERVABILITY_AKTIF = True
            logger.info("[Observability] Console exporter baÅŸlatÄ±ldÄ± â€” tracer aktif.")
            return True
        except Exception as exc:
            logger.warning(
                "[Observability] Console tracer baÅŸlatÄ±lamadÄ±: %s â€” no-op.",
                exc,
            )

    # 3. Geriye uyumlu: env var ile Langfuse
    if _langfuse_kimlik_bilgisi_var():
        try:
            _OBSERVABILITY_AKTIF = _setup_langfuse_tracer(service_name, service_version)
            return _OBSERVABILITY_AKTIF
        except Exception as exc:
            logger.warning(
                "[Observability] Langfuse tracer baÅŸlatÄ±lamadÄ±: %s â€” no-op.",
                exc,
            )

    # 4. No-op (devre dÄ±ÅŸÄ±)
    _setup_noop_tracer(service_name, service_version)
    _OBSERVABILITY_AKTIF = False
    logger.info("[Observability] Observability devre dÄ±ÅŸÄ± â€” no-op tracer kullanÄ±lÄ±yor.")
    return False


# â”€â”€ Tracer kurulumlarÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _setup_noop_tracer(service_name: str, service_version: str) -> None:
    """No-op tracer (hiÃ§bir ÅŸey gÃ¶ndermez)."""
    global _TRACER, _TRACER_PROVIDER

    try:
        from opentelemetry import trace as otel_trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider

        resource = Resource.create(
            {
                "service.name": service_name,
                "service.version": service_version,
            }
        )
        _TRACER_PROVIDER = TracerProvider(resource=resource)
        otel_trace.set_tracer_provider(_TRACER_PROVIDER)
        _TRACER = otel_trace.get_tracer(service_name, service_version)
    except ImportError:
        _TRACER = None
        _TRACER_PROVIDER = None


def _setup_console_tracer(service_name: str, service_version: str) -> None:
    """Console exporter ile tracer baÅŸlat."""
    global _TRACER, _TRACER_PROVIDER

    from opentelemetry import trace as otel_trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export import ConsoleSpanExporter

    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": service_version,
        }
    )
    _TRACER_PROVIDER = TracerProvider(resource=resource)

    exporter = ConsoleSpanExporter()
    span_processor = SimpleSpanProcessor(exporter)
    _TRACER_PROVIDER.add_span_processor(span_processor)
    otel_trace.set_tracer_provider(_TRACER_PROVIDER)

    _TRACER = otel_trace.get_tracer(service_name, service_version)


def _setup_otlp_tracer(service_name: str, service_version: str, endpoint: str) -> bool:
    """OTLP HTTP exporter ile tracer baÅŸlat."""
    global _TRACER, _TRACER_PROVIDER

    from opentelemetry import trace as otel_trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
        OTLPSpanExporter,
    )
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": service_version,
        }
    )
    _TRACER_PROVIDER = TracerProvider(resource=resource)

    exporter = OTLPSpanExporter(
        endpoint=endpoint,
        timeout=10,
    )

    span_processor = BatchSpanProcessor(exporter)
    _TRACER_PROVIDER.add_span_processor(span_processor)
    otel_trace.set_tracer_provider(_TRACER_PROVIDER)

    _TRACER = otel_trace.get_tracer(service_name, service_version)

    logger.info(
        "[Observability] OTLP exporter baÅŸlatÄ±ldÄ± â€” endpoint: %s",
        endpoint,
    )
    return True


def _setup_langfuse_tracer(service_name: str, service_version: str) -> bool:
    """Langfuse OTLP exporter ile tracer baÅŸlat (Basic Auth)."""
    global _TRACER, _TRACER_PROVIDER

    import base64

    from opentelemetry import trace as otel_trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
        OTLPSpanExporter,
    )
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    kimlik_b64 = base64.b64encode(
        f"{LANGFUSE_PUBLIC_KEY}:{LANGFUSE_SECRET_KEY}".encode()
    ).decode("ascii")

    resource = Resource.create(
        {
            "service.name": "langfuse",
            "service.version": service_version,
        }
    )
    _TRACER_PROVIDER = TracerProvider(resource=resource)

    exporter = OTLPSpanExporter(
        endpoint=LANGFUSE_OTLP_TRACES_ENDPOINT,
        headers={
            "Authorization": f"Basic {kimlik_b64}",
            "Content-Type": "application/json",
        },
        timeout=10,
    )

    span_processor = BatchSpanProcessor(exporter)
    _TRACER_PROVIDER.add_span_processor(span_processor)
    otel_trace.set_tracer_provider(_TRACER_PROVIDER)

    _TRACER = otel_trace.get_tracer(service_name, service_version)

    logger.info("[Observability] Langfuse OTLP exporter baÅŸlatÄ±ldÄ± â€” tracer aktif.")
    return True


# â”€â”€ Tracer eriÅŸimi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def get_tracer():
    """Mevcut tracer'Ä± dÃ¶ndÃ¼rÃ¼r; baÅŸlatÄ±lmamÄ±ÅŸsa no-op tracer oluÅŸturur."""
    global _TRACER

    if _TRACER is not None:
        return _TRACER

    setup_observability()
    return _TRACER


tracer = get_tracer  # fonksiyon referansÄ±


def observability_aktif_mi() -> bool:
    """Observability'in aktif olup olmadÄ±ÄŸÄ±nÄ± dÃ¶ndÃ¼rÃ¼r."""
    return _OBSERVABILITY_AKTIF


# â”€â”€ Span oluÅŸturma yardÄ±mcÄ±larÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def span_olustur(
    span_adi: str,
    attributes: Optional[dict[str, Any]] = None,
    span_tipi: str = "internal",
) -> Any:
    """Manuel span oluÅŸtur (context manager olarak kullanÄ±lÄ±r).

    Ã–rnek:
        with span_olustur("session.start", {"user_id": "123"}):
            ...
    """
    _tracer = get_tracer()
    if _tracer is None:
        return nullcontext()

    return _tracer.start_as_current_span(
        span_adi,
        attributes=attributes or {},
        kind=_span_kind(span_tipi),
    )


def _span_kind(span_tipi: str):
    """Span tipi string'ini OpenTelemetry SpanKind'e Ã§evir."""
    try:
        from opentelemetry.trace import SpanKind

        mapping = {
            "internal": SpanKind.INTERNAL,
            "client": SpanKind.CLIENT,
            "server": SpanKind.SERVER,
            "producer": SpanKind.PRODUCER,
            "consumer": SpanKind.CONSUMER,
        }
        return mapping.get(span_tipi, SpanKind.INTERNAL)
    except ImportError:
        return None


# â”€â”€ Token ve maliyet hesaplama yardÄ±mcÄ±larÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# Basit token baÅŸÄ±na maliyet (USD/1K token) â€” en sÄ±k kullanÄ±lan modeller
_TAHMINI_MALIYET: dict[str, dict[str, float]] = {
    "deepseek": {"giris": 0.0005, "cikis": 0.0020},  # deepseek-chat
    "openai": {"giris": 0.00015, "cikis": 0.0006},  # gpt-4o-mini
    "anthropic": {"giris": 0.003, "cikis": 0.015},  # claude-haiku
    "gemini": {"giris": 0.000075, "cikis": 0.0003},  # gemini-1.5-flash
    "groq": {"giris": 0.0001, "cikis": 0.0004},  # llama-3.1-8b
    "xai": {"giris": 0.00015, "cikis": 0.0006},  # grok-2
    "openrouter": {"giris": 0.0005, "cikis": 0.0020},
    "lmstudio": {"giris": 0.0, "cikis": 0.0},  # local
    "ollama": {"giris": 0.0, "cikis": 0.0},  # local
}

_VARSAYILAN_MALIYET = {"giris": 0.001, "cikis": 0.002}


def _token_maliyeti_hesapla(
    provider: str,
    giris_token: int,
    cikis_token: int,
) -> float:
    """Tahmini token maliyetini USD cinsinden hesaplar."""
    fiyat = _TAHMINI_MALIYET.get(provider, _VARSAYILAN_MALIYET)
    giris_maliyet = (giris_token / 1000) * fiyat["giris"]
    cikis_maliyet = (cikis_token / 1000) * fiyat["cikis"]
    return round(giris_maliyet + cikis_maliyet, 6)


def _token_sayisi_tahmin(text: str) -> int:
    """Karakter bazÄ±nda kaba token tahmini (4 karakter â‰ˆ 1 token)."""
    return len(text) // 4 if text else 0


# â”€â”€ LLM span attribute helper â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _llm_span_attr(
    provider: str,
    model: str,
    sistem_prompt: str,
    mesajlar: list,
    yanit: str,
    latency_ms: float,
    success: bool = True,
    hata: Optional[str] = None,
) -> dict[str, Any]:
    """LLM Ã§aÄŸrÄ±sÄ± iÃ§in zengin span attribute'larÄ± oluÅŸturur."""
    giris_token = _token_sayisi_tahmin(sistem_prompt) + sum(
        _token_sayisi_tahmin(str(m)) for m in (mesajlar or [])
    )
    cikis_token = _token_sayisi_tahmin(yanit)
    toplam_token = giris_token + cikis_token
    maliyet = _token_maliyeti_hesapla(provider, giris_token, cikis_token)

    attrs: dict[str, Any] = {
        "span.type": "llm.call",
        "llm.provider": provider,
        "llm.model": model,
        "llm.prompt_tokens": giris_token,
        "llm.completion_tokens": cikis_token,
        "llm.total_tokens": toplam_token,
        "llm.cost_usd": maliyet,
        "llm.latency_ms": round(latency_ms, 2),
        "llm.success": success,
    }

    if hata:
        attrs["error.type"] = (
            type(hata).__name__ if isinstance(hata, Exception) else "Exception"
        )
        attrs["error.message"] = str(hata)

    return attrs


# â”€â”€ LLM Ã§aÄŸrÄ±sÄ± iÃ§in manuel span baÅŸlatma/bitirme API'si â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


class LLMSpan:
    """LLM Ã§aÄŸrÄ±sÄ± iÃ§in span yÃ¶neticisi.

    ``with`` bloÄŸu veya manuel start/end ile kullanÄ±labilir.

    Ã–rnek (manuel):
        span = LLMSpan("dusun", provider="deepseek", model="deepseek-chat")
        span.start(sistem_prompt, mesajlar)
        try:
            yanit = model_cagir(...)
            span.end(yanit)
        except Exception as e:
            span.end_error(e)
    """

    def __init__(
        self,
        name: str = "llm.call",
        provider: str = "",
        model: str = "",
    ):
        self.name = name
        self.provider = provider
        self.model = model
        self._span = None
        self._t0: float = 0.0
        self._sistem_prompt: str = ""
        self._mesajlar: list = []

    def start(self, sistem_prompt: str = "", mesajlar: Optional[list] = None):
        """Span'i baÅŸlat ve zamanÄ± kaydet."""
        self._t0 = time.monotonic()
        self._sistem_prompt = sistem_prompt
        self._mesajlar = mesajlar or []

        _tracer = get_tracer()
        if _tracer is None:
            return

        self._span = _tracer.start_span(
            self.name,
            attributes={
                "span.type": "llm.call",
                "llm.provider": self.provider,
                "llm.model": self.model,
            },
        )

    def end(self, yanit: str = ""):
        """Span'i baÅŸarÄ±yla bitir â€” token/maliyet/latency attribute'larÄ±nÄ± ekle."""
        if self._span is None:
            return

        latency_ms = (time.monotonic() - self._t0) * 1000
        attrs = _llm_span_attr(
            provider=self.provider,
            model=self.model,
            sistem_prompt=self._sistem_prompt,
            mesajlar=self._mesajlar,
            yanit=yanit,
            latency_ms=latency_ms,
            success=True,
        )

        for k, v in attrs.items():
            self._span.set_attribute(k, v)

        self._span.end()
        self._span = None

    def end_error(self, hata: Exception):
        """Span'i hata ile bitir."""
        if self._span is None:
            return

        latency_ms = (time.monotonic() - self._t0) * 1000
        attrs = _llm_span_attr(
            provider=self.provider,
            model=self.model,
            sistem_prompt=self._sistem_prompt,
            mesajlar=self._mesajlar,
            yanit="",
            latency_ms=latency_ms,
            success=False,
            hata=str(hata),
        )

        for k, v in attrs.items():
            self._span.set_attribute(k, v)

        self._span.record_exception(hata)
        _span_set_status(self._span, str(hata))
        self._span.end()
        self._span = None


def _status_error(description: str):
    try:
        from opentelemetry.trace import Status, StatusCode

        return Status(StatusCode.ERROR, description)
    except ImportError:
        return None


def _span_set_status(span, description: str):
    """Span'e hata durumu ata; opentelemetry yoksa sessizce geÃ§."""
    status = _status_error(description)
    if status is not None:
        span.set_status(status)


# â”€â”€ DekoratÃ¶rler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def trace_llm_call(
    span_adi: Optional[str] = None,
    attributes: Optional[dict[str, Any]] = None,
) -> Callable:
    """LLM Ã§aÄŸrÄ±larÄ±nÄ± izlemek iÃ§in dekoratÃ¶r.

    ``llm.call`` span tipinde bir span oluÅŸturur. Span'i fonksiyonun
    etrafÄ±na sarar (start_as_current_span ile) ve ÅŸu attribute'larÄ± ekler:

        - llm.provider
        - llm.model
        - llm.prompt_tokens (tahmini)
        - llm.completion_tokens (tahmini)
        - llm.total_tokens
        - llm.cost_usd (tahmini)
        - llm.latency_ms
        - llm.success

    Hata durumunda span'e hata bilgisi, stack trace ve exception kaydÄ± eklenir.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            _tracer = get_tracer()
            _span_name = span_adi or f"llm.call.{func.__name__}"

            # Provider/model bilgisini self'den al
            provider = ""
            model = ""
            if args and hasattr(args[0], "provider"):
                provider = getattr(args[0], "provider", "")
            if args and hasattr(args[0], "model"):
                model = getattr(args[0], "model", "")

            span_attrs = dict(attributes or {})
            span_attrs.setdefault("span.type", "llm.call")
            span_attrs.setdefault("llm.provider", provider)
            span_attrs.setdefault("llm.model", model)

            if _tracer is not None:
                with _tracer.start_as_current_span(
                    _span_name,
                    attributes=span_attrs,
                    kind=_span_kind("client"),
                ) as span:
                    t0 = time.monotonic()
                    try:
                        result = func(*args, **kwargs)
                        latency_ms = (time.monotonic() - t0) * 1000

                        # Token ve maliyet hesaplama â€” positional ve keyword arg'lari destekle
                        if "sistem_prompt" in kwargs:
                            _sistem_prompt = kwargs["sistem_prompt"]
                        elif len(args) > 1:
                            _sistem_prompt = args[1] if isinstance(args[1], str) else ""
                        else:
                            _sistem_prompt = ""

                        if "mesajlar" in kwargs:
                            _mesajlar = kwargs["mesajlar"]
                        elif len(args) > 2:
                            _mesajlar = (
                                args[2] if isinstance(args[2], (list, tuple)) else []
                            )
                        else:
                            _mesajlar = []

                        if hasattr(result, "metin"):
                            yanit = result.metin
                        elif isinstance(result, dict):
                            yanit = result.get("content", str(result))
                        else:
                            yanit = str(result)

                        giris_token = _token_sayisi_tahmin(_sistem_prompt) + sum(
                            _token_sayisi_tahmin(str(m)) for m in (_mesajlar or [])
                        )
                        cikis_token = _token_sayisi_tahmin(yanit)
                        toplam_token = giris_token + cikis_token
                        maliyet = _token_maliyeti_hesapla(
                            provider, giris_token, cikis_token
                        )

                        span.set_attribute("llm.prompt_tokens", giris_token)
                        span.set_attribute("llm.completion_tokens", cikis_token)
                        span.set_attribute("llm.total_tokens", toplam_token)
                        span.set_attribute("llm.cost_usd", maliyet)
                        span.set_attribute("llm.latency_ms", round(latency_ms, 2))
                        span.set_attribute("llm.success", True)

                        return result

                    except Exception as exc:
                        latency_ms = (time.monotonic() - t0) * 1000
                        span.set_attribute("llm.latency_ms", round(latency_ms, 2))
                        span.set_attribute("llm.success", False)
                        span.set_attribute("error.type", type(exc).__name__)
                        span.set_attribute("error.message", str(exc))
                        span.set_attribute("error.stacktrace", traceback.format_exc())
                        span.record_exception(exc)
                        _span_set_status(span, str(exc))
                        raise
            else:
                # No-op: tracer yoksa direkt Ã§aÄŸÄ±r
                return func(*args, **kwargs)

        return wrapper

    return decorator


def trace_tool_call(
    span_adi: Optional[str] = None,
    attributes: Optional[dict[str, Any]] = None,
) -> Callable:
    """AraÃ§ (tool) Ã§alÄ±ÅŸtÄ±rmalarÄ±nÄ± izlemek iÃ§in dekoratÃ¶r.

    ``tool.execution`` span tipinde bir span oluÅŸturur. Span'e ÅŸu
    attribute'lar eklenir:

        - tool.name
        - tool.args
        - tool.duration_ms
        - tool.result_length

    Hata durumunda span'e hata bilgisi ve stack trace eklenir.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            _tracer = get_tracer()
            _span_name = span_adi or f"tool.execution.{func.__name__}"

            span_attrs = dict(attributes or {})
            span_attrs.setdefault("span.type", "tool.execution")

            # Tool adÄ± ve parametreler (args: self, arac, ham_param, ...)
            if len(args) > 1:
                span_attrs.setdefault("tool.name", str(args[1]))
            if len(args) > 2:
                span_attrs.setdefault("tool.args", str(args[2])[:500])

            if _tracer is not None:
                with _tracer.start_as_current_span(
                    _span_name,
                    attributes=span_attrs,
                ) as span:
                    t0 = time.monotonic()
                    try:
                        result = func(*args, **kwargs)
                        duration_ms = (time.monotonic() - t0) * 1000
                        span.set_attribute("tool.duration_ms", round(duration_ms, 2))
                        if result is not None:
                            span.set_attribute("tool.result_length", len(str(result)))
                        span.set_attribute("tool.success", True)
                        return result

                    except Exception as exc:
                        duration_ms = (time.monotonic() - t0) * 1000
                        span.set_attribute("tool.duration_ms", round(duration_ms, 2))
                        span.set_attribute("tool.success", False)
                        span.set_attribute("error.type", type(exc).__name__)
                        span.set_attribute("error.message", str(exc))
                        span.set_attribute("error.stacktrace", traceback.format_exc())
                        span.record_exception(exc)
                        _span_set_status(span, str(exc))
                        raise
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator


# â”€â”€ Skill ve oturum span'leri iÃ§in baÄŸlam yÃ¶neticileri â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def trace_skill_load(skill_adi: str, **extra_attrs: Any):
    """Skill yÃ¼kleme span'i iÃ§in baÄŸlam yÃ¶neticisi.

    ``skill.load`` span tipi.

    Ã–rnek:
        with trace_skill_load("web_arama", kategori="arama"):
            skill_yukle(...)
    """
    attrs = {
        "span.type": "skill.load",
        "skill.name": skill_adi,
        **extra_attrs,
    }
    return span_olustur(f"skill.load.{skill_adi}", attributes=attrs)


def trace_session_start(oturum_id: str, **extra_attrs: Any):
    """Oturum baÅŸlatma span'i iÃ§in baÄŸlam yÃ¶neticisi.

    ``session.start`` span tipi.

    Ã–rnek:
        with trace_session_start("abc-123", kullanici="marko"):
            oturum_baslat(...)
    """
    attrs = {
        "span.type": "session.start",
        "session.id": oturum_id,
        **extra_attrs,
    }
    return span_olustur(f"session.start.{oturum_id}", attributes=attrs)


def trace_session_end(oturum_id: str, **extra_attrs: Any):
    """Oturum bitiÅŸ span'i iÃ§in baÄŸlam yÃ¶neticisi.

    ``session.end`` span tipi.

    Ã–rnek:
        with trace_session_end("abc-123", message_count=5, total_tokens=1500):
            oturum_kapat(...)
    """
    attrs = {
        "span.type": "session.end",
        "session.id": oturum_id,
        **extra_attrs,
    }
    return span_olustur(f"session.end.{oturum_id}", attributes=attrs)


# â”€â”€ Durum sorgulama â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def observability_durum() -> dict[str, Any]:
    """Observability sisteminin mevcut durumunu dÃ¶ndÃ¼rÃ¼r."""
    return {
        "aktif": _OBSERVABILITY_AKTIF,
        "langfuse_public_key_var": bool(LANGFUSE_PUBLIC_KEY),
        "langfuse_secret_key_var": bool(LANGFUSE_SECRET_KEY),
        "tracer_yuklu": _TRACER is not None,
        "provider_yuklu": _TRACER_PROVIDER is not None,
    }
