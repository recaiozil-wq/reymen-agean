"""ReYMeN tools.tts_tool shim â€” ReYMeN TTS fonksiyonlarÄ±nÄ± ReYMeN voice_engine'e yÃ¶nlendirir.

Bu modÃ¼l, ReYMeN Agent'in tools/tts_tool.py'sini taklit eder.
TÃ¼m iÅŸlevler ReYMeN'in voice_engine.py'sine yÃ¶nlendirilir.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# TTS Config
# ---------------------------------------------------------------------------


def _load_tts_config() -> Dict[str, Any]:
    """ReYMeN TTS config formatÄ±nÄ± taklit eder. Env var'dan okur."""
    return {
        "provider": os.getenv("REYMEN_TTS_PROVIDER", "edge"),
        "voice": os.getenv("REYMEN_TTS_VOICE", "tr-TR-AhmetNeural"),
        "model": os.getenv("REYMEN_TTS_MODEL", "tts-1"),
    }


def _get_provider(config: Dict[str, Any]) -> str:
    """ReYMeN _get_provider fonksiyonunu taklit eder."""
    return config.get("provider", "edge")


def _import_elevenlabs() -> None:
    """ElevenLabs SDK kontrolÃ¼ â€” yoksa ImportError."""
    try:
        import elevenlabs  # noqa: F401
    except ImportError:
        raise ImportError("elevenlabs not installed. pip install elevenlabs")


def _import_sounddevice() -> None:
    """sounddevice kontrolÃ¼ â€” yoksa ImportError."""
    try:
        import sounddevice  # noqa: F401
    except ImportError:
        raise ImportError("sounddevice not installed. pip install sounddevice")


def stream_tts_to_speaker(
    text_queue,
    voice: str = "alloy",
    model: str = "tts-1",
    stream_callback=None,
    stop_event=None,
) -> None:
    """ReYMeN stream_tts_to_speaker â€” ReYMeN voice_engine'e yÃ¶nlendirir.

    Basit implementasyon: ses dosyasÄ±na kaydedip oynatÄ±r.
    GerÃ§ek streaming iÃ§in elevenlabs veya baÅŸka bir streaming TTS gerekir.
    """
    try:
        from reymen.arac.voice_engine import VoiceRegistry

        registry = VoiceRegistry()
        text = ""
        while not stop_event or not stop_event.is_set():
            try:
                chunk = text_queue.get(timeout=1)
                if chunk is None:
                    break
                text += chunk
            except Exception:
                if text and stop_event and stop_event.is_set():
                    break
                continue

        if text.strip():
            result = registry.seslendir("edge", text, voice)
            logger.info("TTS completed: %s", result[:80] if result else "empty")
    except Exception as e:
        logger.warning("stream_tts_to_speaker failed: %s", e)


# ---------------------------------------------------------------------------
# text_to_speech_tool â€” ana TTS fonksiyonu
# ---------------------------------------------------------------------------


def text_to_speech_tool(
    text: str,
    voice: Optional[str] = None,
    output_path: Optional[str] = None,
    provider: Optional[str] = None,
) -> str:
    """ReYMeN text_to_speech_tool â€” ReYMeN voice_engine'e yÃ¶nlendirir.

    Args:
        text: Sese Ã§evrilecek metin
        voice: Ses adÄ± (opsiyonel)
        output_path: Ã‡Ä±ktÄ± dosyasÄ± yolu (opsiyonel)
        provider: TTS saÄŸlayÄ±cÄ±sÄ± ('edge', 'openai', vb.)

    Returns:
        str: JSON formatÄ±nda sonuÃ§
    """
    import json

    try:
        from reymen.arac.voice_engine import VoiceRegistry

        registry = VoiceRegistry()
        effective_provider = provider or os.getenv("REYMEN_TTS_PROVIDER", "edge")
        effective_voice = voice or os.getenv("REYMEN_TTS_VOICE", "tr-TR-AhmetNeural")

        result = registry.seslendir(effective_provider, text, effective_voice)

        if (
            output_path
            and result
            and not result.startswith("[")
            and os.path.exists(result)
        ):
            import shutil

            shutil.copy(result, output_path)

        return json.dumps({"success": True, "output": result})
    except Exception as e:
        logger.error("text_to_speech_tool error: %s", e)
        return json.dumps({"success": False, "error": str(e)})


# ---------------------------------------------------------------------------
# speech_to_text_tool
# ---------------------------------------------------------------------------


def speech_to_text_tool(
    audio_path: str,
    language: str = "tr",
    provider: Optional[str] = None,
) -> str:
    """ReYMeN speech_to_text_tool â€” ReYMeN voice_engine'e yÃ¶nlendirir.

    Args:
        audio_path: Ses dosyasÄ± yolu
        language: Dil kodu
        provider: STT saÄŸlayÄ±cÄ±sÄ± ('whisper', 'openai', vb.)

    Returns:
        str: JSON formatÄ±nda sonuÃ§
    """
    import json

    try:
        from reymen.arac.voice_engine import VoiceRegistry

        registry = VoiceRegistry()
        effective_provider = provider or os.getenv("REYMEN_STT_PROVIDER", "whisper")

        result = registry.yaziya_cevir(effective_provider, audio_path, language)

        return json.dumps({"success": True, "text": result})
    except Exception as e:
        logger.error("speech_to_text_tool error: %s", e)
        return json.dumps({"success": False, "error": str(e)})
