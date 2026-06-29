# Mimari

## Genel Yapi

```
reymen/
+-- cereyan/           # Core motor ve ogrenme
|   +-- motor.py       # Ana arac motoru
|   +-- conversation_loop.py  # Konusma dongusu
|   +-- continuous_learning.py # Surekli ogrenme
+-- ag/                # Provider ve iletisim
|   +-- model_provider_router.py  # Model yonlendirme
|   +-- failover_chain.py        # Hata yedekleme
|   +-- gateway_*                  # Gateway bilesenleri
|   +-- delegasyon.py             # Goev devretme
+-- sistem/            # Sistem bilesenleri
|   +-- plugins/       # Plugin dizini
|   +-- hot_reload.py  # Runtime reload
|   +-- tts_tool_text.py  # Metin seslendirme
|   +-- stt_tool.py    # Ses tanima
+-- guvenlik/          # Guevenlik
|   +-- oauth_sistemi.py
|   +-- guardrails.py
|   +-- docker_sandbox.py
+-- hafiza/            # Bellek
|   +-- vektor_bellek.py  # Vector memory
|   +-- bellek_yonetici.py
+-- arac/              # Arac motorlari
|   +-- browser_engine.py
|   +-- image_gen_engine.py
|   +-- video_gen_engine.py
|   +-- web_search_engine.py
+-- web_ui/            # Web arayuecue
+-- core/              # Core servisler
+-- reymen_cli/        # CLI komutlari
```

## Veri Akisi

1. Kullanici mesaji -> conversation_loop.py
2. Skill aktivasyonu -> active_skill_tracker.py
3. Provider secimi -> model_provider_router.py
4. LLM yaniti + arac cagrilari -> motor.py
5. Arac sonuclari -> kullaniciya iletilir
6. Ogrenme -> continuous_learning.py / self_improve.py

## Teknoloji Yigini

- **Dil:** Python 3.11+
- **LLM:** DeepSeek, OpenAI, Anthropic, Gemini, Groq, Ollama, LM Studio
- **Veritabani:** SQLite (FTS5 + trigram)
- **Vector DB:** ChromaDB + TF-IDF
- **Web UI:** FastAPI + HTMX
- **TUI:** Rich + prompt_toolkit
- **TTS:** edge-tts
- **STT:** faster-whisper
- **Browser:** Playwright MCP
- **Göruntu:** FAL.ai, OpenAI, xAI
- **Video:** moviepy, FAL.ai
