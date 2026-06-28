---
name: software-development_money-printer-turbo_references_api-key-varsa-normal-gemini_tts-a-r
description: API key varsa normal gemini_tts çağır
title: "Software Development Money Printer Turbo References Api Key Varsa Normal Gemini Tts A R"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | API key varsa normal gemini_tts çağır |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# API key varsa normal gemini_tts çağır
    parts = voice_name.split(":")
    if len(parts) >= 2:
        voice = parts[1].split("-")[0]
        return gemini_tts(text, voice, voice_rate, voice_file, voice_volume)
```

**UYARI:** `azure_tts_v1()` 4 parametre alır (voice_volume YOK). 5 parametreyle çağırma TypeError alırsın.
