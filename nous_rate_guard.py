# -*- coding: utf-8 -*-
"""SHIM — agent/nous_rate_guard.py yönlendirir + ReYMeN API uyum katmanı.

beyin.py şu üç fonksiyonu kullanır:
  rate_guard_izin_ver(provider) -> bool   — istek yapılabilir mi?
  rate_guard_basla(provider)              — istek başlamadan çağrılır
  rate_guard_bitir(provider)              — istek bittikten sonra çağrılır

Hermes API'si (agent/nous_rate_guard.py):
  nous_rate_limit_remaining() -> float|None
  record_nous_rate_limit(...)
  clear_nous_rate_limit()
"""
from agent.nous_rate_guard import *  # noqa: F401, F403
from agent.nous_rate_guard import nous_rate_limit_remaining  # explicit

# Private name export — test patching için
import importlib as _imp_nrg, sys as _sys_nrg
_src_nrg = _imp_nrg.import_module('agent.nous_rate_guard')
_sys_nrg.modules[__name__].__dict__.update(
    {k: v for k, v in vars(_src_nrg).items() if k.startswith('_') and not k.startswith('__')}
)

import threading as _threading
import time as _time

_kilit = _threading.Lock()
_aktif_istekler: dict = {}  # provider → başlangıç zamanı


def rate_guard_izin_ver(provider: str) -> bool:
    """True → istek yapılabilir, False → hız sınırı aktif (atla)."""
    kalan = nous_rate_limit_remaining()
    return kalan is None  # None = rate limit yok


def rate_guard_basla(provider: str) -> None:
    """İstek başlamadan önce başlangıç zamanını kaydet."""
    with _kilit:
        _aktif_istekler[provider] = _time.monotonic()


def rate_guard_bitir(provider: str) -> None:
    """İstek bittikten sonra kaydı temizle."""
    with _kilit:
        _aktif_istekler.pop(provider, None)
