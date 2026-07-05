# -*- coding: utf-8 -*-
"""Transcription Provider Registry — STT saglayicilarini yonetir.

Hermes agent/transcription_registry.py'den adapte edilmistir.
"""
from __future__ import annotations

import logging
import threading
from typing import Dict, List, Optional

from reymen.transcription_provider import TranscriptionProvider

logger = logging.getLogger(__name__)

_providers: Dict[str, TranscriptionProvider] = {}
_lock = threading.Lock()


def register_provider(provider: TranscriptionProvider) -> None:
    """Bir STT provider'i kaydet."""
    if not isinstance(provider, TranscriptionProvider):
        raise TypeError(f"Beklenen: TranscriptionProvider, alinan: {type(provider).__name__}")
    name = provider.name
    with _lock:
        _providers[name] = provider
    logger.debug("STT provider '%s' kaydedildi", name)


def list_providers() -> List[TranscriptionProvider]:
    """Kayitli tum provider'lari listele."""
    with _lock:
        return sorted(_providers.values(), key=lambda p: p.name)


def get_provider(name: str) -> Optional[TranscriptionProvider]:
    """Adi verilen provider'i getir."""
    with _lock:
        return _providers.get(name.strip())


def _reset_for_tests() -> None:
    """Registry'i temizle (test)."""
    with _lock:
        _providers.clear()
