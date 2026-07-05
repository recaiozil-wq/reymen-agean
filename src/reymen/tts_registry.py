# -*- coding: utf-8 -*-
"""TTS Provider Registry.

Hermes agent/tts_registry.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
import threading
from typing import Dict, List, Optional
from reymen.tts_provider import TTSProvider

logger = logging.getLogger(__name__)
_providers: Dict[str, TTSProvider] = {}
_lock = threading.Lock()

def register_provider(provider: TTSProvider) -> None:
    with _lock:
        _providers[provider.name] = provider

def list_providers() -> List[TTSProvider]:
    with _lock:
        return sorted(_providers.values(), key=lambda p: p.name)

def get_provider(name: str) -> Optional[TTSProvider]:
    with _lock:
        return _providers.get(name.strip())
