# -*- coding: utf-8 -*-
"""transcription_tools.py — Ses Yazilimi (STT) Araci.

Whisper (local) veya API ile ses dosyasini metne cevirir.
"""

import os
from pathlib import Path
from typing import Any, Optional


def sesi_metne_cevir(ses_dosyasi: str, model: str = "base") -> str:
    """Ses dosyasini metne cevir.

    Args:
        ses_dosyasi: Ses dosyasi yolu (.wav, .mp3, .m4a)
        model: Whisper model boyutu (tiny, base, small, medium, large)

    Returns:
        Metin veya hata mesaji
    """
    dosya = Path(ses_dosyasi)
    if not dosya.exists():
        return f"[STT]: Dosya bulunamadi: {ses_dosyasi}"

    try:
        import whisper
        import warnings
        warnings.filterwarnings("ignore")

        print(f"[STT] Yukleniyor: {model} model...")
        model_whisper = whisper.load_model(model)
        print(f"[STT] Cozumleniyor: {dosya.name}...")
        sonuc = model_whisper.transcribe(str(dosya), language="tr")

        metin = sonuc.get("text", "").strip()
        if not metin:
            return "[STT]: Metin cozulemedi."
        return f"[STT]: {metin}"
    except ImportError:
        return "[STT]: openai-whisper kurulu degil."
    except Exception as e:
        return f"[STT]: Hata: {e}"


if __name__ == "__main__":
    print(sesi_metne_cevir("test.wav"))


# ── Upstream Hermes uyumluluk stublari ─────────────────────────────────


def _get_provider() -> Optional[str]:
    """Aktif STT saglayicisini dondur — upstream Hermes uyumluluk."""
    return None


def transcribe_audio(audio_path: str, **kwargs) -> str:
    """Ses dosyasini metne cevir — upstream Hermes uyumluluk."""
    return sesi_metne_cevir(audio_path)


MAX_FILE_SIZE: int = 25 * 1024 * 1024  # 25 MB
SUPPORTED_FORMATS: tuple = (".wav", ".mp3", ".m4a", ".ogg", ".flac")
GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
OPENAI_BASE_URL: str = "https://api.openai.com/v1"
COMMAND_STT_OUTPUT_FORMATS: tuple = ("text", "json", "srt", "vtt")
DEFAULT_COMMAND_STT_LANGUAGE: str = "tr"
DEFAULT_COMMAND_STT_OUTPUT_FORMAT: str = "text"
DEFAULT_COMMAND_STT_TIMEOUT_SECONDS: int = 120


def _transcribe_local_command(audio_path: str, **kwargs) -> str:
    """Local komut ile ses tanima — upstream Hermes uyumluluk."""
    return sesi_metne_cevir(audio_path)
