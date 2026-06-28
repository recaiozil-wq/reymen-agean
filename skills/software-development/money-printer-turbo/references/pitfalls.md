---
skill_id: 0382b30a0834
usage_count: 1
last_used: 2026-06-16
---
## Pitfalls

1. **.venv'de pip yok** → önemli değil, `uv sync` kullan
2. **`uv sync` "VIRTUAL_ENV mismatch" uyarısı** → zararsız
3. **`voice_name` boş** → Edge TTS hatası. CLI'da her zaman `--voice-name` ver
4. **WebUI'da Gemini sesi seçili** → API key yoksa Edge TTS'e düşer (voice.py'ye yama gerekli)
5. **Config.toml sürekli sıfırlanıyor** → WebUI `save_config()` tüm config'i yeniden yazar; elle eklenen `deepseek_api_key`, `voice_name` silinir, `llm_provider` `"openai"`'a döner. **Çözüm:** CLI kullanmadan önce `taskkill /F /IM python.exe` ile tüm Python'ları öldür (**⚠️ her şeyi kapatır**), config'i düzelt, CLI'ı çalıştır. WebUI kapalıyken config bozulmaz.
6. **Port 8501 dolu** → `--server.port=8510` dene
7. **Backend 8080 bind hatası** → eski process'i öldür
8. **MoviePy 2.x `subclip` AttributeError** → `subclip()` yok, `subclipped()` kullan
9. **Gemini TTS fallback parametre hatası** → `azure_tts_v1(text, voice, rate, file)` 4 parametre alır, 5 değil