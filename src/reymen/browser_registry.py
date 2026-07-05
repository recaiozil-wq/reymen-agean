# -*- coding: utf-8 -*-
"""Browser Provider Registry.

Hermes agent/browser_registry.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
import threading
from typing import Dict, List, Optional
from reymen.browser_provider import BrowserProvider

logger = logging.getLogger(__name__)
_providers: Dict[str, BrowserProvider] = {}
_lock = threading.Lock()

def register_provider(provider: BrowserProvider) -> None:
    if not isinstance(provider, BrowserProvider):
        raise TypeError(f"Beklenen: BrowserProvider, alinan: {type(provider).__name__}")
    with _lock:
        _providers[provider.name] = provider

def list_providers() -> List[BrowserProvider]:
    with _lock:
        return sorted(_providers.values(), key=lambda p: p.name)

def get_provider(name: str) -> Optional[BrowserProvider]:
    with _lock:
        return _providers.get(name.strip())

def _resolve(name: Optional[str] = None) -> Optional[BrowserProvider]:
    """Aktif provider'i coz."""
    if name and name != "local":
        p = get_provider(name)
        if p:
            return p
    for p in list_providers():
        try:
            if p.is_available():
                return p
        except Exception:
            continue
    return None

def _reset_for_tests() -> None:
    with _lock:
        _providers.clear()
