# -*- coding: utf-8 -*-
"""
observability.py — OpenTelemetry + Langfuse ile gözlemlenebilirlik katmanı.

LLM çağrıları, araç çalıştırmaları, skill yüklemeleri ve oturum başlatmaları
için span'ler oluşturur. LANGFUSE_PUBLIC_KEY ve LANGFUSE_SECRET_KEY ortam
değişkenleri varsa Langfuse OTLP exporter'a veri gönderir, yoksa sessizce
devre dışı kalır (no-op tracer).

Kullanım:
    from reymen.core.observability import (
        setup_observability,
        trace_llm_call,
        trace_tool_call,
        tracer,
    )

    # Uygulama başlangıcında bir kez çağır
    setup_observability()

    # Dekoratör olarak
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
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

# ── Langfuse ortam değişkenleri ──────────────────────────────────────────────
LANGFUSE_PUBLIC_KEY = os.environ.get("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY = os.environ.get("LANGFUSE_SECRET_KEY", "")

# Langfuse OTLP endpoint'leri
LANGFUSE_OTLP_TRACES_ENDPOINT = os.environ.get(
    "LANGFUSE_OTLP_TRACES_ENDPOINT",
    "https://cloud.langfuse.com/api/public/otlp/v1/traces",
)
LANGFUSE_OTLP_METRICS_ENDPOINT = os.environ.get(
    "LANGFUSE_OTLP_METRICS_ENDPOINT",
    "https://cloud.langfuse.com/api/public/otlp/v1/metrics",
)

# Langfuse'un istediği özel enjektör başlıkları için
# service.name = langfuse olarak set edildiğinde Langfuse OTLP alıcısı
# Authorization başlığını Basic (public_key:secret_key) olarak oluşturur.

_TRACER = None  # type: ignore[assignment]
_TRACER_PROVIDER = None  # type: ignore[assignment]
_OBSERVABILITY_AKTIF = False


def _langfuse_kimlik_bilgisi_var() -> bool:
    """Langfuse kimlik bilgileri ortamda mevcut mu?"""
    return bool(LANGFUSE_PUBLIC_KEY) and bool(LANGFUSE_SECRET_KEY)


def setup_observability(
    service_name: str = "reymen-agent",
    service_version: str = "1.0.0",
) -> bool:
    """OpenTelemetry tracer'ı başlat.

    LANGFUSE_PUBLIC_KEY ve LANGFUSE_SECRET_KEY ortam değişkenleri
    tanımlıysa Langfuse OTLP exporter kullanılır. Aksi halde no-op
    tracer döner (hiçbir span gönderilmez).

    Args:
        service_name:    OpenTelemetry servis adı.
        service_version: OpenTelemetry servis versiyonu.

    Returns:
        True ise observability aktif, False ise devre dışı.
    """
    global _TRACER, _TRACER_PROVIDER, _OBSERVABILITY_AKTIF

    if _TRACER is not None:
        return _OBSERVABILITY_AKTIF  # Zaten başlatılmış

    if not _langfuse_kimlik_bilgisi_var():
        logger.info(
            "[Observability] LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY "
            "tanımlı değil — observability devre dışı (no-op tracer)."
        )
        _OBSERVABILITY_AKTIF = False
        _setup_noop_tracer(service_name, service_version)
        return False

    try:
        _OBSERVABILITY_AKTIF = _setup_langfuse_tracer(
            service_name, service_version
        )
    except Exception as exc:
        logger.warning(
            "[Observability] Langfuse tracer başlatılamadı: %s — "
            "no-op tracer kullanılıyor.",
            exc,
        )
        _OBSERVABILITY_AKTIF = False
        _setup_noop_tracer(service_name, service_version)

    return _OBSERVABILITY_AKTIF


def _setup_noop_tracer(service_name: str, service_version: str) -> None:
    """No-op tracer (hiçbir şey göndermez)."""
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
        # OpenTelemetry SDK kurulu değil — tamamen no-op
        _TRACER = None
        _TRACER_PROVIDER = None


def _setup_langfuse_tracer(
    service_name: str,
    service_version: str,
) -> bool:
    """Langfuse OTLP exporter ile tracer başlat."""
    global _TRACER, _TRACER_PROVIDER

    from opentelemetry import trace as otel_trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
        OTLPSpanExporter,
    )
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    # Langfuse Basic Auth: public_key:secret_key → Base64
    import base64

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

    # Langfuse OTLP HTTP exporter
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

    logger.info(
        "[Observability] Langfuse OTLP exporter başlatıldı — "
        "tracer aktif."
    )
    return True


def get_tracer():
    """Mevcut tracer'ı döndürür; başlatılmamışsa no-op tracer oluşturur."""
    global _TRACER

    if _TRACER is not None:
        return _TRACER

    # İlk çağrıda otomatik setup
    setup_observability()
    return _TRACER


# Modül seviyesinde tracer erişimi: get_tracer() ile aynı
tracer = get_tracer  # fonksiyon referansı — çağrı: tracer()


def observability_aktif_mi() -> bool:
    """Observability'in aktif olup olmadığını döndürür."""
    return _OBSERVABILITY_AKTIF


# ── Span oluşturma yardımcıları ──────────────────────────────────────────────


def span_olustur(
    span_adi: str,
    attributes: Optional[dict[str, Any]] = None,
    span_tipi: str = "internal",
) -> Any:
    """Manuel span oluştur (context manager olarak kullanılır).

    Örnek:
        with span_olustur("session.start", {"user_id": "123"}):
            ...
    """
    _tracer = get_tracer()
    if _tracer is None:
        # No-op context manager
        from contextlib import nullcontext

        return nullcontext()

    return _tracer.start_as_current_span(
        span_adi,
        attributes=attributes or {},
        kind=_span_kind(span_tipi),
    )


def _span_kind(span_tipi: str):
    """Span tipi string'ini OpenTelemetry SpanKind'e çevir."""
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
        return None  # type: ignore[return-value]


# ── Dekoratörler ─────────────────────────────────────────────────────────────


def trace_llm_call(
    span_adi: Optional[str] = None,
    attributes: Optional[dict[str, Any]] = None,
) -> Callable:
    """LLM çağrılarını izlemek için dekoratör.

    ``llm.call`` span tipinde bir span oluşturur. Span'e şu attribute'lar
    eklenir:
        - model
        - provider
        - prompt_tokens (tahmini)
        - completion_tokens (tahmini)
        - latency_ms

    Hata durumunda span'e hata bilgisi ve stack trace eklenir.

    Örnek:
        @trace_llm_call()
        def dusun(self, sistem_prompt, mesajlar):
            ...

        @trace_llm_call(span_adi="custom.llm.call")
        def ozel_cagri(self, ...):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            _tracer = get_tracer()
            _span_name = span_adi or f"llm.call.{func.__name__}"

            # Sonucu al
            t0 = time.monotonic()
            try:
                result = func(*args, **kwargs)
                latency_ms = (time.monotonic() - t0) * 1000

                # Span attribute'larını belirle
                span_attrs = dict(attributes or {})

                # args[0] = self (Beyin instance)
                if args and hasattr(args[0], "provider"):
                    span_attrs.setdefault("provider", getattr(args[0], "provider", ""))
                if args and hasattr(args[0], "model"):
                    span_attrs.setdefault("model", getattr(args[0], "model", ""))

                # Token tahmini (LLMYanitMeta veya string)
                if hasattr(result, "tahmini_token") and hasattr(result, "metin"):
                    # LLMYanitMeta dönüşü
                    span_attrs.setdefault(
                        "prompt_tokens", getattr(result, "tahmini_token", 0)
                    )
                    span_attrs.setdefault(
                        "completion_tokens", len(getattr(result, "metin", "")) // 4
                    )
                elif isinstance(result, str):
                    # String yanıt: prompt'u kwargs/mesajlardan al
                    mesajlar = kwargs.get("mesajlar", [])
                    sistem_prompt = kwargs.get("sistem_prompt", "")
                    prompt_tokens = (
                        len(sistem_prompt)
                        + sum(len(str(m)) for m in mesajlar)
                    ) // 4
                    completion_tokens = len(result) // 4
                    span_attrs.setdefault("prompt_tokens", prompt_tokens)
                    span_attrs.setdefault(
                        "completion_tokens", completion_tokens
                    )

                span_attrs.setdefault("latency_ms", round(latency_ms, 2))
                span_attrs.setdefault("span.type", "llm.call")

                if _tracer is not None:
                    _tracer.start_span(
                        _span_name,
                        attributes=span_attrs,
                    ).end()

                return result

            except Exception as exc:
                latency_ms = (time.monotonic() - t0) * 1000

                error_attrs = dict(attributes or {})
                error_attrs.setdefault("latency_ms", round(latency_ms, 2))
                error_attrs.setdefault("span.type", "llm.call")
                error_attrs.setdefault("error.type", type(exc).__name__)
                error_attrs.setdefault("error.message", str(exc))
                error_attrs.setdefault(
                    "error.stacktrace", traceback.format_exc()
                )

                if args and hasattr(args[0], "provider"):
                    error_attrs.setdefault(
                        "provider", getattr(args[0], "provider", "")
                    )
                if args and hasattr(args[0], "model"):
                    error_attrs.setdefault(
                        "model", getattr(args[0], "model", "")
                    )

                if _tracer is not None:
                    _tracer.start_span(
                        f"error.{_span_name}",
                        attributes=error_attrs,
                    ).end()

                raise

        return wrapper

    return decorator


def trace_tool_call(
    span_adi: Optional[str] = None,
    attributes: Optional[dict[str, Any]] = None,
) -> Callable:
    """Araç (tool) çalıştırmalarını izlemek için dekoratör.

    ``tool.execution`` span tipinde bir span oluşturur. Span'e şu
    attribute'lar eklenir:
        - tool.name
        - tool.args
        - latency_ms

    Hata durumunda span'e hata bilgisi ve stack trace eklenir.

    Örnek:
        @trace_tool_call()
        def calistir(self, arac, ham_param):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            _tracer = get_tracer()
            _span_name = span_adi or f"tool.execution.{func.__name__}"

            t0 = time.monotonic()
            try:
                result = func(*args, **kwargs)
                latency_ms = (time.monotonic() - t0) * 1000

                span_attrs = dict(attributes or {})
                span_attrs.setdefault("span.type", "tool.execution")

                # Tool adı ve parametreler
                if len(args) > 1:
                    span_attrs.setdefault("tool.name", str(args[1]))
                if len(args) > 2:
                    span_attrs.setdefault(
                        "tool.args", str(args[2])[:500]
                    )  # args çok uzun olabilir

                span_attrs.setdefault("latency_ms", round(latency_ms, 2))

                if result is not None:
                    span_attrs.setdefault(
                        "tool.result_length", len(str(result))
                    )

                if _tracer is not None:
                    _tracer.start_span(
                        _span_name,
                        attributes=span_attrs,
                    ).end()

                return result

            except Exception as exc:
                latency_ms = (time.monotonic() - t0) * 1000

                error_attrs = dict(attributes or {})
                error_attrs.setdefault("span.type", "tool.execution")
                error_attrs.setdefault("error.type", type(exc).__name__)
                error_attrs.setdefault("error.message", str(exc))
                error_attrs.setdefault(
                    "error.stacktrace", traceback.format_exc()
                )
                error_attrs.setdefault("latency_ms", round(latency_ms, 2))

                if len(args) > 1:
                    error_attrs.setdefault("tool.name", str(args[1]))
                if len(args) > 2:
                    error_attrs.setdefault(
                        "tool.args", str(args[2])[:500]
                    )

                if _tracer is not None:
                    _tracer.start_span(
                        f"error.{_span_name}",
                        attributes=error_attrs,
                    ).end()

                raise

        return wrapper

    return decorator


# ── Skill ve oturum span'leri için bağlam yöneticileri ────────────────────────


def trace_skill_load(skill_adi: str, **extra_attrs: Any):
    """Skill yükleme span'i için bağlam yöneticisi.

    ``skill.load`` span tipi.

    Örnek:
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
    """Oturum başlatma span'i için bağlam yöneticisi.

    ``session.start`` span tipi.

    Örnek:
        with trace_session_start("abc-123", kullanci="marko"):
            oturum_baslat(...)
    """
    attrs = {
        "span.type": "session.start",
        "session.id": oturum_id,
        **extra_attrs,
    }
    return span_olustur(f"session.start.{oturum_id}", attributes=attrs)


def observability_durum() -> dict[str, Any]:
    """Observability sisteminin mevcut durumunu döndürür."""
    return {
        "aktif": _OBSERVABILITY_AKTIF,
        "langfuse_public_key_var": bool(LANGFUSE_PUBLIC_KEY),
        "langfuse_secret_key_var": bool(LANGFUSE_SECRET_KEY),
        "tracer_yuklu": _TRACER is not None,
        "provider_yuklu": _TRACER_PROVIDER is not None,
        "endpoint": LANGFUSE_OTLP_TRACES_ENDPOINT,
    }
