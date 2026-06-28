---
skill_id: 3f719741e28c
usage_count: 1
last_used: 2026-06-16
---
# API key varsa normal gemini_tts çağır
    parts = voice_name.split(":")
    if len(parts) >= 2:
        voice = parts[1].split("-")[0]
        return gemini_tts(text, voice, voice_rate, voice_file, voice_volume)
```

**UYARI:** `azure_tts_v1()` 4 parametre alır (voice_volume YOK). 5 parametreyle çağırma TypeError alırsın.