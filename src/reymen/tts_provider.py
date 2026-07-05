# -*- coding: utf-8 -*-
"""TTS (Text-to-Speech) Provider ABC.

Hermes agent/tts_provider.py'den adapte edilmistir.
"""
from __future__ import annotations
import abc
from typing import Optional

class TTSProvider(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str: ...
    @abc.abstractmethod
    def speak(self, text: str, voice: Optional[str] = None) -> Optional[bytes]: ...

class EdgeTTSProvider(TTSProvider):
    @property
    def name(self): return "edge"
    def speak(self, text, voice=None):
        try:
            import edge_tts
            import asyncio
            v = voice or "tr-TR-AhmetNeural"
            coro = edge_tts.Communicate(text, v)
            return asyncio.run(coro.stream())
        except Exception:
            return None
