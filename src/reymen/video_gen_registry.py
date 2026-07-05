# -*- coding: utf-8 -*-
"""Video uretim provider registry.

Hermes agent/video_gen_registry.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
import threading
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)
_providers: Dict[str, Any] = {}
_lock = threading.Lock()

def register_provider(name: str, provider_fn) -> None:
    with _lock:
        _providers[name] = provider_fn

def list_providers() -> List[str]:
    with _lock:
        return sorted(_providers.keys())

def get_provider(name: str):
    with _lock:
        return _providers.get(name.strip())

def _reset_for_tests() -> None:
    with _lock:
        _providers.clear()
