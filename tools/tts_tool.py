# -*- coding: utf-8 -*-
"""tts_tool.py — Metni sese cevir (edge-tts)."""

import subprocess
import tempfile
import os
from pathlib import Path
from typing import Any


def run(metin: str = "", ses: str = "tr-TR-AhmetNeural") -> str:
    if not metin or not metin.strip():
        return "[Hata]: metin parametresi gerekli."

    # mktemp() deprecated + race condition — mkstemp kullan
    fd, tmp_path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)  # edge-tts kendi açacak; fd'yi bırak

    try:
        subprocess.run(
            [
                "edge-tts",
                "--voice", ses,
                "--text", metin.strip(),
                "--write-media", tmp_path,
            ],
            check=True,
            capture_output=True,
            timeout=30,
        )
        return f"[Tamam] Ses kaydedildi: {tmp_path}"
    except FileNotFoundError:
        # Temp dosyası boş kaldı, temizle
        Path(tmp_path).unlink(missing_ok=True)
        return "[Hata]: edge-tts kurulu degil (pip install edge-tts)"
    except subprocess.CalledProcessError as e:
        Path(tmp_path).unlink(missing_ok=True)
        stderr = e.stderr.decode("utf-8", errors="replace").strip()
        return f"[Hata]: edge-tts basarisiz — {stderr}"
    except Exception as e:
        Path(tmp_path).unlink(missing_ok=True)
        return f"[Hata]: {e}"


def motor_kaydet(motor) -> None:
    motor._plugin_arac_kaydet("TTS", run, "Metni sese cevir (edge-tts)")


# ── Upstream Hermes uyumluluk stublari ─────────────────────────────────


COMMAND_TTS_OUTPUT_FORMATS: tuple = ("wav", "mp3", "ogg")
DEFAULT_GEMINI_TTS_MODEL: str = "models/gemini-2-flash-tts"
DEFAULT_GEMINI_TTS_VOICE: str = "en-US-Standard-A"
DEFAULT_KITTENTTS_MODEL: str = "en_US-amy-medium"
DEFAULT_KITTENTTS_VOICE: str = "en_US-amy-medium"
DEFAULT_MISTRAL_TTS_MODEL: str = "mistral-tts"
FALLBACK_MAX_TEXT_LENGTH: int = 4000
DEFAULT_PIPER_VOICE: str = "en_US-amy-medium"


def _generate_edge_tts(text: str, voice: str = "", **kwargs) -> bytes:
    """Edge TTS ile ses sentezi — upstream Hermes uyumluluk."""
    return b""


def _generate_openai_tts(text: str, voice: str = "", **kwargs) -> bytes:
    """OpenAI TTS ile ses sentezi — upstream Hermes uyumluluk."""
    return b""


def _generate_xai_tts(text: str, voice: str = "", **kwargs) -> bytes:
    """XAI TTS ile ses sentezi — upstream Hermes uyumluluk."""
    return b""


def _strip_markdown_for_tts(text: str) -> str:
    """Markdown temizleme — upstream Hermes uyumluluk."""
    import re
    return re.sub(r"[*_`#\[\]]", "", text)
