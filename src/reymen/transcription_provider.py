# -*- coding: utf-8 -*-
"""Transcription Provider ABC — Ses dosyasindan metin cikarma arayuzu.

Hermes agent/transcription_provider.py'den adapte edilmistir.
ReYMeN'e ozgu: plugin sistemi yok, dogrudan voice engine kullanir.
"""
from __future__ import annotations

import abc
from typing import Any, Dict, List, Optional


class TranscriptionProvider(abc.ABC):
    """Ses dosyasindan metin cikarma (STT) icin abstract base class."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Provider adi. Orn: local, groq, openai"""

    def is_available(self) -> bool:
        """Kullanilabilir mi? API key kontrolu."""
        return True

    @abc.abstractmethod
    def transcribe(self, file_path: str, *, model: Optional[str] = None,
                   language: Optional[str] = None, **extra: Any) -> Dict[str, Any]:
        """Ses dosyasini metne cevir.

        Returns:
            {"success": bool, "transcript": str, "provider": str, "error": str}
        """


class LocalWhisperProvider(TranscriptionProvider):
    """Yerel Whisper (faster-whisper) ile transkripsiyon."""

    @property
    def name(self) -> str:
        return "local"

    def is_available(self) -> bool:
        try:
            import faster_whisper  # noqa
            return True
        except ImportError:
            return False

    def transcribe(self, file_path: str, *, model: Optional[str] = None,
                   language: Optional[str] = None, **extra: Any) -> Dict[str, Any]:
        try:
            from faster_whisper import WhisperModel
            model_name = model or "base"
            whisper = WhisperModel(model_name, device="cpu", compute_type="int8")
            segments, _ = whisper.transcribe(file_path, language=language)
            transcript = " ".join(seg.text for seg in segments)
            return {"success": True, "transcript": transcript, "provider": "local"}
        except Exception as e:
            return {"success": False, "transcript": "", "error": str(e), "provider": "local"}
