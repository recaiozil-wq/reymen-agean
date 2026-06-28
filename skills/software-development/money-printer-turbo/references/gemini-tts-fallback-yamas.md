---
skill_id: 67b6fe54ec8e
usage_count: 1
last_used: 2026-06-16
---
## Gemini TTS Fallback Yaması

`app/services/voice.py` dosyasında `tts()` fonksiyonunda `is_gemini_voice` bloğu:

Önce API key kontrol et, yoksa Edge TTS'e düş:

```python
elif is_gemini_voice(voice_name):
    gemini_key = config.app.get("gemini_api_key", "")
    if not gemini_key:
        logger.warning(f"Gemini API key not set, falling back to Edge TTS")
        fallback_voice = "tr-TR-EmelNeural"
        return azure_tts_v1(text, fallback_voice, voice_rate, voice_file)