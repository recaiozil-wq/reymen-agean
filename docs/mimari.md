# Architecture

## Overall Structure

```
reymen/
+-- cereyan/           # Core motor and learning
|   +-- motor.py       # Main tool engine
|   +-- conversation_loop.py  # Conversation loop
|   +-- continuous_learning.py # Continuous learning
+-- ag/                # Provider and communication
|   +-- model_provider_router.py  # Model routing
|   +-- failover_chain.py        # Error failover
|   +-- gateway_*                  # Gateway components
|   +-- delegasyon.py             # Task delegation
+-- sistem/            # System components
|   +-- plugins/       # Plugin directory
|   +-- hot_reload.py  # Runtime reload
|   +-- tts_tool_text.py  # Text-to-speech
|   +-- stt_tool.py    # Speech recognition
+-- guvenlik/          # Security
|   +-- oauth_sistemi.py
|   +-- guardrails.py
|   +-- docker_sandbox.py
+-- hafiza/            # Memory
|   +-- vektor_bellek.py  # Vector memory
|   +-- bellek_yonetici.py
+-- arac/              # Tool engines
|   +-- browser_engine.py
|   +-- image_gen_engine.py
|   +-- video_gen_engine.py
|   +-- web_search_engine.py
+-- web_ui/            # Web interface
+-- core/              # Core services
+-- reymen_cli/        # CLI commands
```

## Data Flow

1. User message -> conversation_loop.py
2. Skill activation -> active_skill_tracker.py
3. Provider selection -> model_provider_router.py
4. LLM response + tool calls -> motor.py
5. Tool results -> delivered to user
6. Learning -> continuous_learning.py / self_improve.py

## Technology Stack

- **Language:** Python 3.11+
- **LLM:** DeepSeek, OpenAI, Anthropic, Gemini, Groq, Ollama, LM Studio
- **Database:** SQLite (FTS5 + trigram)
- **Vector DB:** ChromaDB + TF-IDF
- **Web UI:** FastAPI + HTMX
- **TUI:** Rich + prompt_toolkit
- **TTS:** edge-tts
- **STT:** faster-whisper
- **Browser:** Playwright MCP
- **Image:** FAL.ai, OpenAI, xAI
- **Video:** moviepy, FAL.ai
