---
name: software-development_money-printer-turbo_references_gemini-tts-fallback-yamas
description: Gemini TTS Fallback Yaması
title: "Software Development Money Printer Turbo References Gemini Tts Fallback Yamas"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Gemini TTS Fallback Yaması |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

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
