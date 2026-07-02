# 📖 ReYMeN API Reference

> Version: 0.9.0 · Python 3.11+

---

## 📦 Main Modules

### reymen (root package)

`reymen/__init__.py`

```
__version__ = "0.9.0"
```

**Submodules:** `cost_tracker`, `platform_adapter`, `tui`, `self_improve`, `kanban`, `video_tools`, `a2a`

---

## 🧠 LLM Layer — `reymen.cereyan.beyin`

**`Beyin(config)`** — Multi-provider LLM connection layer. 15+ providers, automatic failover chain.

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `dusun(sistem_prompt, mesajlar, model=None, provider=None)` | `sistem_prompt: str`, `mesajlar: list[dict]`, `model: Optional[str]`, `provider: Optional[str]` | `str` | LLM'den yanıt üret; fallback zincirine göre sağlayıcılar denenir. Tek seferlik provider geçersiz kılma destekler. |
| `uret(sistem_prompt, mesajlar, **kwargs)` | `sistem_prompt: str`, `mesajlar: list[dict]`, `**kwargs` | `str` | `dusun()` için geriye dönük uyumlu alias. |
| `uret_v2(sistem_prompt, mesajlar, tools=None)` | `sistem_prompt: str`, `mesajlar: list[dict]`, `tools: Optional[list]` | `dict` | Native function calling destekli LLM çağrısı. Döner: `{"role", "content", "tool_calls"}` |
| `dusun_stream(sistem_prompt, mesajlar, model=None)` | `sistem_prompt: str`, `mesajlar: list[dict]`, `model: Optional[str]` | `Generator[str, None, None]` | Streaming LLM yanıtı — token token yield eder. OpenAI-uyumlu + Anthropic. |
| `iptal_et()` | — | `None` | Devam eden API çağrısını iptal et. |
| `sifirla()` | — | `None` | İptal olayını sıfırla — yeni görev başlamadan önce çağır. |
| `provider_cagir(provider, model, mesajlar, sistem_prompt="")` | `provider: str`, `model: str`, `mesajlar: list[dict]`, `sistem_prompt: str` | `str` | Herhangi bir provider'a API çağrısı yap. Config'den base_url ve api_key okur. |
| `fc_destekleniyor()` | — | `bool` | Aktif provider'ın native function calling destekleyip desteklemediğini döndürür. |

**Desteklenen Sağlayıcılar:** LM Studio, DeepSeek, OpenAI, Anthropic, Groq, Azure OpenAI, AWS Bedrock, Google Gemini / Vertex AI, Moonshot, Ollama, OpenRouter, xAI/Grok, Together AI, Fireworks AI, Mistral AI, Cohere, Perplexity

**Yardımcı Veri Yapıları:**

| Sınıf | Alanlar | Açıklama |
|-------|---------|----------|
| `SaglayCiAdim(provider, model, base_url, api_key)` | `provider: str`, `model: str`, `base_url: str`, `api_key: str` | Fallback zincirindeki tek bir sağlayıcı adımı. |
| `LLMYanitMeta(metin, provider, model, sure_sn, tahmini_token)` | `metin: str`, `provider: str`, `model: str`, `sure_sn: float`, `tahmini_token: int` | `_cagir()` dönüş değeri: metin + basit üstveri. |

**Örnek Kullanım:**
```python
from reymen.cereyan.beyin import Beyin
beyin = Beyin(config={"default_provider": "deepseek", "providers": {...}})
yanit = beyin.dusun("Sen yardımcı bir asistansın.", [{"role": "user", "content": "Merhaba!"}])
```

---

## 🔄 Conversation Loop — `reymen.cereyan.conversation_loop`

**`GorevCozucu(motor=None, beyin=None, max_turns=30)`** — Intelligent task solving with 7-source ensemble comparison.

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `coz(goal, context=None)` | `goal: str`, `context: Optional[str]` | `str` | Simple API (legacy) — tek seferlik LLM sorgusu. |
| `run_conversation(goal, context=None, provider=None)` | `goal: str`, `context: Optional[str]`, `provider: Optional[str]` | `str` | Advanced API (ReYMeN pipeline). |

**Flow:** QUERY → OnceHafiza → Session search → Skill scan → Ensemble (7 sources) → Save → Response

**Önemli Dahili Metodlar:**
| Metod | Açıklama |
|-------|----------|
| `_arac_calistir(tool_name, params)` | Araç çağrılarını çalıştırır, tool_calls döngüsünü yönetir |
| `_context_sikistir()` | Context eşik aşıldığında otomatik sıkıştırma |
| `_api_cagir(messages, tools)` | API çağrısı yap, interruptible thread ile |
| `_hata_isle(e)` | Hata yönetimi, failover kararları |
| `_response_uret()` | Yanıt üret, kaydet, logla |

**Entegre Sistemler:** NudgeModel, ProaktifDenetci, RulesEngine, SkillActivator, Delegasyon, ContextCompressor, SessionSearch, OnceHafiza, PromptCaching, CircuitBreaker, MessageBroker

---

## 🎯 Action Engine — `reymen.cereyan.motor`

**`Motor(backend_mode="local", hafiza_collection=None, config=None)`** — Captures actions from LLM output, routes through ToolRegistry + plugins.

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `calistir(tool, raw_param)` | `tool: str`, `raw_param: str` | `str` | Execute tool — ham string parametre ile. |
| `calistir_fc(tool, args)` | `tool: str`, `args: dict` | `str` | Execute in function-calling format (JSON args). |
| `tools_schema_al(max=64)` | `max: int` | `list` | Generate OpenAI-compatible tool schema listesi. |
| `tum_arac_tanimini_al()` | — | `list` | Return all tool definitions from registry + plugins. |
| `gorev_coz(task_path)` | `task_path: str` | `str` | Resolve task file (YAML/JSON task definition). |
| `eylemi_ayristir(llm_output)` | `llm_output: str` | `tuple` | Extract action name+param from LLM output (`Action: TOOL(param)`). |
| `musait_araclar(toolset=None)` | `toolset: Optional[str]` | `list` | List available tools. |
| `hook_kaydet(olay, fn)` | `olay: str`, `fn: callable` | `None` | Register motor hook (async). |
| `broker_durum()` | — | `dict` | MessageBroker durum raporu. |
| `gorev_coz_pipeline(gorev_tanimi, script_path="")` | `gorev_tanimi: str`, `script_path: str` | `str` | Pipeline ile görev çözümü: GÖREV → PLAN → DOĞRULA → KOD → TEST → İNCELE → KAYDET. |

**Motor Tarafından Otomatik Yüklenen Araç Modülleri:** CUA araçları, Browser araçları, Web arama, Kod çalıştırma, TTS/STT, MCP, Kanban, Delegasyon, Obsidian, HyperFrames, Görsel analiz, Görsel üretim, OAuth, Provider yönetimi, Session search, Memory, Skill aktivasyonu, Cron, Gateway, A2A/ACP, Plugin sistemi

---

## 🧩 Hook System — `reymen.cereyan.hook_dispatcher`

Function-based hook system for 8 event types.

### Event Types

| Event | Trigger | When |
|------|---------|------|
| `on_session_start` | `oturum_baslat_tetikle()` | Session starts |
| `on_session_end` | `oturum_bitir_tetikle()` | Session ends |
| `on_turn_start` | `tur_baslat_tetikle()` | Each turn starts |
| `on_turn_end` | `tur_bitir_tetikle()` | Each turn ends |
| `on_tool_call` | `arac_cagri_tetikle()` | Before tool is called |
| `on_tool_result` | `arac_sonuc_tetikle()` | After tool result is received |
| `on_error` | `hata_tetikle()` | When error occurs |
| `on_context_compress` | `context_sikistirma_tetikle()` | Before context compression |

### Functions

| Function | Description |
|---------|----------|
| `hook_kaydet(event, callback)` | Register hook callback |
| `hook_kaldir(event, callback)` | Remove hook (returns bool) |
| `hook_cagir(event, **kwargs)` | Fire all callbacks |
| `hook(event)` | Decorator: `@hook("on_session_start")` |
| `kayitli_hooklar()` | Summary of registered hooks |
| `tum_hooklari_temizle()` | Clear all hooks (test isolation) |

---

## 💬 Message Broker — `reymen.cereyan.broker`

**`MessageBroker`** — queue.Queue-based, thread-safe, 18 message types.

| Method | Description |
|-------|----------|
| `abone_ol(consumer_id, message_types, callback)` | Subscribe to message type |
| `abone_ol_liste(consumer_id, message_types, callback)` | Subscribe with list |
| `yayinla(message)` | Publish message |
| `yayinla_basit(type, data, source="")` | Simple publish |
| `baslat()` | Start broker |
| `durdur()` | Stop broker |
| `durum()` | Status report |

**18 Message Types:** ERROR, SOLVE_SEARCH, SOLVE_FOUND, TASK_ASSIGN, TASK_RECEIVED, TASK_COMPLETE, TASK_CANCEL, TOOL_CALL, TOOL_RESULT, INFO, WARNING, STOP, TAKEOVER, BROADCAST, AUDIO, VIDEO, LOG, CONTROL

---

## 💰 Cost Tracking — `reymen.cost_tracker`

SQLite-based API spending tracker.

### `CostTracker`

| Method | Description |
|-------|----------|
| `compute_cost(model, input_tokens, output_tokens)` | Calculate cost |
| `record(model, input_tokens, output_tokens, cost, provider="", metadata=None)` | Add record |
| `summary()` | Summary report |
| `dump_log(limit=50)` | Recent records |
| `reset()` | Delete all records |
| `iter_records()` | Iterate over all records |

### Module Functions

`record_usage()`, `summary()`, `dump_log()`, `reset()`, `set_db_path()`, `set_price_table()`

---

## 📊 Kanban — `reymen.kanban`

### `Board`

WIP-limited, priority-sorted, deadline-supported kanban board.

| Method | Description |
|-------|----------|
| `add(card, column="backlog")` | Add card |
| `move(card_id, target_column)` | Move card |
| `set_status(card_id, status)` | Update status |
| `prioritize(card_id, priority)` | Change priority |
| `find(card_id)` | Find card |
| `complete(card_id)` | Mark as completed |
| `summary()` | Board summary |
| `save()` / `load()` | Persistent storage |
| `to_json()` / `from_dict()` | Serialization |

### Worker API

`kanban_create()`, `kanban_show()`, `kanban_complete()`, `kanban_block()`, `kanban_unblock()`, `kanban_comment()`, `kanban_heartbeat()`, `kanban_claim()`, `kanban_list()`, `kanban_summary()`, `kanban_delete_card()`

---

## 🌍 Platform Adapter — `reymen.platform_adapter`

### `PlatformAdapter` (base class)

| Method | Description |
|-------|----------|
| `info()` | Platform info |
| `translate_path(path)` | Translate path (e.g. C:\ → /mnt/c/) |
| `run(command)` | Run command |

**Subclasses:** `NativeAdapter`, `WSLAdapter`, `KaliAdapter`

### Module Functions

`detect()`, `translate_path()`, `run()`, `is_wsl_available()`, `list_wsl_distros()`

---

## 🔄 Self-Improvement — `reymen.self_improve`

### `SelfImprover`

| Method | Description |
|-------|----------|
| `record(metric)` | Record metric |
| `history()` | History metrics |
| `trend()` | Trend analysis |
| `low_quality_steps(threshold=0.5)` | Low quality steps |
| `auto_improve()` | Auto-improvement suggestion |
| `reset()` | Reset |

### Module Functions

`evaluate()`, `suggest_fix()`, `record_step()`, `record_step_with_cost()`, `report()`, `reset_history()`

---

## 🪟 TUI — `reymen.tui`

Rich-based terminal interface.

| Function | Description |
|---------|----------|
| `with_spinner(text)` | Spinner context manager |
| `progress_bar(iterable, description="")` | Progress bar |
| `info()` / `success()` / `warning()` / `error()` | Colored messages |
| `panel(content, title="")` | Rich panel |
| `table(columns, rows)` | Rich table |

### `StatusBar`
Single-line status bar.

---

## 🎬 Video Tools — `reymen.video_tools`

yt-dlp + ffmpeg wrapper.

| Function | Description |
|---------|----------|
| `download(url, format="best")` | Download video |
| `probe(path)` | Video info |
| `convert(source, target)` | Format conversion |
| `extract_audio(source, target)` | Extract audio |
| `cut(source, start, end, target)` | Cut video |

### Classes

`VideoInfo` — Downloaded video info (dataclass)
`FFmpegResult` — ffmpeg result (dataclass)

---

## 🌐 Web UI — `reymen.web_ui`

FastAPI + HTMX management panel.

| Route | Description |
|-------|----------|
| `/` | Home page |
| `/api/durum` | System status |
| `/api/gateway/restart` | Restart gateway |
| `/api/loglar` | System logs |
| `/api/bot/test` | Bot test |

---

## 🤝 A2A Messaging — `reymen.a2a`

Thread-safe queue-based inter-agent messaging protocol.

### Classes

#### `MessageType(str, Enum)`
Message types: `TEXT`, `TASK`, `RESULT`, `QUERY`, `RESPONSE`, `ERROR`, `BROADCAST`, `HEARTBEAT`

#### `Message(sender, receiver, content, type=TEXT, id=uuid, reply_to=None, timestamp, metadata={})`

| Method | Returns | Description |
|-------|---------|----------|
| `as_dict()` | `dict` | Convert to dictionary |
| `reply(content, msg_type=None)` | `Message` | Create reply message |

#### `Broker()`

| Method | Returns | Description |
|-------|---------|----------|
| `register(agent_id)` | `None` | Register agent |
| `unregister(agent_id)` | `None` | Remove agent |
| `is_registered(agent_id)` | `bool` | Check if registered |
| `send(message)` | `None` | Send message (throws `A2AError`) |
| `broadcast(sender, content, exclude=None)` | `list[str]` | Broadcast to all agents |
| `receive(agent_id, timeout=None, block=True)` | `Message\|None` | Receive message |
| `peek(agent_id)` | `Message\|None` | Peek without consuming |
| `inbox_size(agent_id)` | `int` | Pending messages |
| `set_handler(agent_id, handler)` | `None` | Set handler |
| `clear_handler(agent_id)` | `None` | Clear handler |
| `message_log()` | `list[Message]` | All delivered messages |
| `stats()` | `dict` | Broker statistics |
| `reset()` | `None` | Clear all inboxes and log |

#### `Agent(agent_id, broker, on_message=None)`

| Method | Returns | Description |
|-------|---------|----------|
| `send(receiver, content, msg_type=TEXT, reply_to=None, metadata=None)` | `Message` | Send message |
| `broadcast(content, exclude=None)` | `list[str]` | Broadcast |
| `reply(original, content)` | `Message` | Reply to message |
| `receive(timeout=None, block=True)` | `Message\|None` | Receive |
| `peek()` | `Message\|None` | Peek |
| `inbox_size` | `int` (property) | Pending messages |
| `set_handler(handler)` | `None` | Set handler |
| `clear_handler()` | `None` | Clear handler |
| `close()` | `None` | Unregister |

### Error Class

**`A2AError(RuntimeError)`** — A2A messaging error (e.g. target agent not registered)

---

## 🛠️ Tool Layer — `reymen.arac`

### BrowserTool — `araclar_gelismis.py`

Headless Chromium (Playwright) + urllib fallback.

| Method | Description |
|-------|----------|
| `ac(url)` | Open page, read text |
| `screenshot(url="", output="screenshot.png")` | Take screenshot |
| `js_calistir(url="", js="document.title")` | Execute JavaScript |
| `tikla(selector)` | Click element |
| `fill(selector, value)` | Fill form field |
| `type_text(selector, value)` | Type character by character |
| `select_option(selector, value)` | Select dropdown option |
| `wait_for(selector, timeout=10)` | Wait for element |
| `wait_for_text(text, timeout=10)` | Wait for text |
| `hover(selector)` | Hover over element |
| `scroll(dx=0, dy=300)` | Scroll page |
| `scroll_to(selector)` | Scroll to element |
| `back()` / `forward()` / `reload()` | History management |
| `new_tab(url="")` | Open new tab |
| `switch_tab(index)` | Switch to tab |
| `close_tab(index=-1)` | Close tab |
| `tabs_list()` | List open tabs |
| `snapshot(max=3000)` | Return page text |
| `html(max=3000)` | Return page HTML |
| `title()` / `url()` | Title / URL |
| `dialog_accept()` / `dialog_dismiss()` | Dialog management |
| `network_requests(limit=10)` | Monitor network requests |
| `cookies()` / `clear_state()` | Cookie/state management |
| `kapat()` | Close browser |

### TarayiciKontrol — `araclar_tarayici.py`

Simple browser that opens/closes on each operation.

| Method | Description |
|-------|----------|
| `sayfa_ac_ve_oku(url, selector=None)` | Open URL, return text |
| `tikla_ve_yaz(url, click_selector, input_selector, text)` | Click + type |

---

## 🧠 Core Modules

### Model Adapter — `reymen.core.model_adapter`

| Class | Description |
|-------|----------|
| `ModelAdapter` (protocol) | `complete(prompt) -> str` |
| `OllamaAdapter` | localhost:11434 |
| `OpenAICompatAdapter` | LM Studio / DeepSeek / OpenAI |
| `AnthropicAdapter` | Claude API |

`get_active_adapter()` — Select adapter via REYMEN_MODEL env.

### Orchestrator — `reymen.core.orchestrator`

| Function | Description |
|---------|----------|
| `run_script(path)` | Run Python script |
| `solve_step(step_name, script_path)` | Solve single step (max 3 retries) |
| `solve_all(steps)` | Solve all steps sequentially |
| `coz_hata(error, code, name)` | Ask LLM about error |

### Learning — `reymen.core.ogrenme`

Error→solution memory (SQLite, TTL=30 days).

| Function | Description |
|---------|----------|
| `imza_uret(error)` | Generate error signature |
| `cozum_bul(signature)` | Search for saved solution |
| `cozum_kaydet(signature, error_type, error_summary, solution_code)` | Save solution |
| `tablo_olustur()` | Create DB tables |
| `istatistik()` | Learning statistics |
| `ttl_temizle()` | Clean old records |

### Session Search — `reymen.core.session_search`

FTS5-based conversation history search.

| Function | Description |
|---------|----------|
| `session_ara(query, limit=5)` | FTS5 search |
| `session_listele(limit=10)` | Recent sessions |
| `session_mesajlari(session_id)` | Session messages |
| `session_istatistik()` | Statistics |

### MCP Server — `reymen.core.mcp_server`

Model Context Protocol server.

| Function | Description |
|---------|----------|
| `tool_kaydet(name, func, description, schema)` | Register tool |
| `tool_sil(name)` | Remove tool |
| `get_tools()` | All tools |
| `resource_kaydet(uri, reader)` | Register resource |
| `prompt_kaydet(name, generator)` | Register prompt |

**Default Tools:** ReYMeN_status, memory_search, session_search, file_read, file_write, shell

---

## 🔐 Security — `reymen.guvenlik`

| Module | Description |
|-------|----------|
| `file_safety.py` | `guvenli_mi(path)` — file security check |
| `path_security.py` | `yol_dogrula(path)` — path validation |
| `redact.py` | `tam_temizle(message)` — PII redaction |
| `guardrails.py` | Output guardrails |
| `guvenli_sandbox.py` | `guvenli_calistir(code)` — isolated Python execution |
| `security_engine.py` | Threat detection engine |
| `anayasa_denetci.py` | Constitutional AI audit |

---

## 🧠 Memory — `reymen.hafiza`

| Module | Description |
|-------|----------|
| `once_hafiza.py` | Vector-based priority memory |
| `session_db.py` | FTS5 session database |
| `context_compressor.py` | Context compression |
| `memory_manager.py` | Memory manager |
| `bounded_memory.py` | Bounded memory |
| `gorev_hafiza.py` | Task history |
| `vektorel_hafiza.py` | Vector memory (ChromaDB) |

---

## 🪟 Windows — `reymen.windows`

| Module | Description |
|-------|----------|
| `windows_entegrasyon.py` | Windows system integration |
| `trajectory.py` | Windows event tracking |
| `trajectory_compressor.py` | Trajectory compression |
| `tor_otomasyonu.py` | Tor browser automation |
| `browser_camofox.py` | Firefox-based browser |
| `otonom_nisan_olusturucu.py` | Autonomous target creator |
| `screenshot_bot.py` | Screenshot bot |
| `nisan_yakala.py` | Target capture tool |

---

## ⚙️ CLI — `reymen.sistem`

| Module | Description |
|-------|----------|
| `cli_main.py` | Main CLI (4,857 lines) |
| `cli_agent.py` | Agent lifecycle (2,618 lines) |
| `cli_session.py` | Session management |
| `cli_display.py` | Display mixin |
| `cli_stream.py` | Streaming mixin |
| `cli_commands.py` | Command management |
| `run_agent.py` | Agent runner (4,858 lines) |
| `main.py` | AIAgentOrchestrator (1,582 lines) |

---

## 🧩 Sub-CLI Commands

| Command | Description |
|-------|----------|
| `reymen status` | System status |
| `reymen cost` | View costs |
| `reymen platform` | Platform info |
| `reymen quality` | Quality report |
| `reymen kanban` | Kanban management |
| `reymen video` | Video operations |
| `reymen a2a` | A2A test |
| `reymen web` | Start Web UI |
| `reymen backup` | Backup |
| `reymen cron` | Cron job management |
| `reymen config` | Configuration |
| `reymen debug` | Debug tools |
| `reymen doctor` | System diagnostics |
| `reymen kural` | Rule management (list, ekle, sil, kontrol) |
| `reymen setup` | First-time setup wizard |
| `reymen update` | Self-update system |

---

## 🔍 FTS5 Session Search — `reymen.cereyan.session_search`

**`SessionSearch(db_yolu=None)`** — FTS5-based session message search engine. Independent module (separate from session_db.py).

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `save(session_id, message, role="user")` | `session_id: str`, `message: str`, `role: str` | `bool` | Save a message to the FTS5 table. Thread-safe. |
| `search(query, limit=10, session_id=None)` | `query: str`, `limit: int`, `session_id: Optional[str]` | `list[dict]` | Full-text search with FTS5. Supports AND/OR/prefix/exact phrase syntax. |
| `session_mesajlari(session_id, limit=50)` | `session_id: str`, `limit: int` | `list[dict]` | Get all messages for a specific session. |
| `istatistik()` | — | `dict` | Total record count and statistics. |

**Modül Seviyesi Fonksiyonlar:**
```python
session_search_al(db_yolu=None) -> SessionSearch  # Singleton instance (thread-safe)
save(session_id, message, role="user") -> bool       # Easy save via singleton
search(query, limit=10, session_id=None) -> list      # Easy search via singleton
```

**Örnek:**
```python
from reymen.cereyan.session_search import SessionSearch
ss = SessionSearch()
ss.save("session-001", "Kullanıcı merhaba dedi", "user")
sonuclar = ss.search("merhaba", limit=5)
```

---

## 🗜️ Memory Compaction — `reymen.cereyan.memory_compaction`

MEMORY.md / USER.md 50K compaction system. Automatically prunes files approaching 50,000 characters by priority scoring.

| Fonksiyon | Parameters | Returns | Description |
|-----------|-----------|---------|-------------|
| `memory_compaction_check(zorla=False)` | `zorla: bool` | `dict` | MEMORY.md ve USER.md'de compaction kontrolü yap. Rapor döndürür. |
| `cache_tazele()` | — | `dict` | @lru_cache ile cache'lenmiş fonksiyonları temizle (prompt_assembly). |

**Compaction Rapor Formatı:**
```json
{
  "tarih": "2026-07-02 12:00:00",
  "zorla": false,
  "dosyalar": {
    "MEMORY.md": {"onceki_karakter": 45000, "sonraki_karakter": 28000, "silinen_entry": 5, ...},
    "USER.md": {"onceki_karakter": 12000, "sonraki_karakter": 12000, "compaction_yapildi": false, ...}
  },
  "toplam_budanan_karakter": 17000,
  "toplam_silinen_entry": 5
}
```

**Öncelik Sıralaması:** ZORUNLU KURAL (100) → KURAL (90) → ONEMLI (80) → OGRENILEN (70) → TERCIH (60) → BILGI (50) → NOT (40) → HATIRLATMA (30) → GOREV (20) → LOG (10)

**Örnek:**
```python
from reymen.cereyan.memory_compaction import memory_compaction_check
rapor = memory_compaction_check()           # Lightweight check
rapor = memory_compaction_check(zorla=True) # Force compaction
```

---

## 🕵️ NudgeModel (Stealth User Modelling) — `reymen.cereyan.nudge_model`

**`NudgeModel(veritabani_yolu=None)`** — Hermes Honcho-like stealth user modelling system. Silently observes user preferences, response style, technical level, language preference, and tool usage frequency.

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `gozlemle(mesaj, yanit)` | `mesaj: str`, `yanit: str` | `dict` | Observe a user-agent interaction: analyzes style, tech level, language, tool usage. |
| `kullanici_modeli_al()` | — | `dict` | Return current user model with confidence scores. |
| `sistem_prompu_ekle()` | — | `str` | Generate text block to append to system prompt. |
| `nudge()` | — | `str` | Return a context-appropriate reminder/suggestion. |
| `rapor_uret()` | — | `str` | Generate a summary report for the user. |

**Gözlem Kategorileri:**
- Stil: resmi, samimi, teknik, kisa, detayli, komut, soru, hata_bildirimi
- Teknik seviye: 1 (çok düşük) → 5 (çok yüksek)
- Dil: tr, en
- Araç kullanımı: terminal, dosya_oku, dosya_yaz, ara, web, kod_calistir, diger
- Duygu tonu: pozitif, negatif, notr, acil

**Örnek:**
```python
from reymen.cereyan.nudge_model import NudgeModel
nm = NudgeModel()
nm.gozlemle("merhaba, nasılsın?", "iyiyim teşekkürler!")
model = nm.kullanici_modeli_al()
prompt_ek = nm.sistem_prompu_ekle()
hatirlatma = nm.nudge()
```

---

## ✅ Proaktif Kontrol — `reymen.cereyan.proaktif_kontrol`

**`ProaktifDenetci(db_yol=None)`** — Analyzes missing aspects after each question/answer. Learns from repeated missing categories.

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `soru_cevap_analiz(soru, cevap)` | `soru: str`, `cevap: str` | `dict` | Analyze QA pair: detect requested categories, missing items, quality score. |
| `eksik_bul(analiz=None)` | `analiz: Optional[dict]` | `list[str]` | Returns missing items from the current analysis. |
| `ders_al(analiz=None)` | `analiz: Optional[dict]` | `None` | Extract lessons from the analysis, track repeated missing items. |
| `proaktif_uyari(soru)` | `soru: str` | `Optional[str]` | Generate warning from past missing items for similar questions. |
| `en_sik_eksikler(limit=5)` | `limit: int` | `list[tuple]` | Most frequently repeated missing categories. |
| `durum_raporu()` | — | `str` | Short status report with statistics. |

**Modül Seviyesi Fonksiyonlar:**
```python
proaktif_baslat() -> ProaktifDenetci  # Singleton başlat
soru_sonrasi_kontrol(soru, cevap) -> dict  # Main function called after each QA
```

**Eksik Kategorileri:** tablo, kaynak, ornek, nicel_veri, edge_case, karsilastirma, adim_adim, neden, ne_zaman, nerede

**Örnek:**
```python
from reymen.cereyan.proaktif_kontrol import soru_sonrasi_kontrol
analiz = soru_sonrasi_kontrol("Bana Linux komutlarını tablo halinde sırala", "ls komutu dizin listeler")
print(analiz["eksikler"])  # ["tablo"]
```

---

## 📋 Delegate Task Tool — `reymen.tools.delegate_task_tool`

ThreadPoolExecutor-based parallel sub-agent delegation. Runs sub-agents in parallel, each with a separate Beyin instance.

| Fonksiyon | Parameters | Returns | Description |
|-----------|-----------|---------|-------------|
| `delegate_task(gorev_tanimlari, baglam_genel="", max_paralel=5, timeout=120, max_adim=10)` | `gorev_tanimlari: str (JSON)`, `baglam_genel: str`, `max_paralel: int`, `timeout: int`, `max_adim: int` | `str` | Alt ajanları ThreadPoolExecutor ile paralel çalıştırır. Özet metin döndürür. |
| `motor_kaydet(motor)` | `motor: Motor` | `None` | Motor'a DELEGATE_TASK aracını kaydeder (otomatik çağrılır). |

**Veri Yapıları:**
| Sınıf | Alanlar | Açıklama |
|-------|---------|----------|
| `AltGorevSonuc(gorev, task_id, basarili, sonuc, hata, sure_sn, adim_sayisi)` | `gorev: str`, `task_id: str`, `basarili: bool`, `sonuc: str`, `hata: str`, `sure_sn: float`, `adim_sayisi: int` | Single sub-task result. |
| `DelegasyonSonuc(parent_task_id, toplam_gorev, basarili, basarisiz, sonuclar, toplam_sure_sn, ozet)` | `parent_task_id: str`, `toplam_gorev: int`, `basarili: int`, `basarisiz: int`, `sonuclar: list[AltGorevSonuc]`, `toplam_sure_sn: float`, `ozet: str` | Complete delegation result. |

**Örnek:**
```python
from reymen.tools.delegate_task_tool import delegate_task
gorevler = '[{"gorev": "Dosyayı oku ve özetle", "baglam": "test.py"}, {"gorev": "Web ara", "baglam": "yapay zeka"}]'
sonuc = delegate_task(gorevler, max_paralel=3, timeout=60)
print(sonuc)
```

---

## 🎬 HyperFrames Video Generation — `reymen.tools.hyperframes_tool`

Renders HTML + CSS + JS animations frame-by-frame with Playwright and assembles into video with FFmpeg.

| Fonksiyon | Parameters | Returns | Description |
|-----------|-----------|---------|-------------|
| `hyperframes_olustur(template, params, cikti, fps=30, sure=5)` | `template: str`, `params: dict`, `cikti: str`, `fps: int`, `sure: int` | `dict` | Create video from template. Döner: `{"basarili": bool, "video_yolu": str, ...}` |
| `motor_kaydet(motor)` | `motor: Motor` | `None` | Motor'a HYPERFRAMES aracını kaydeder. |

**Şablonlar:**
| Şablon | Parametreler | Açıklama |
|--------|-------------|----------|
| `METIN_ANIMASYONU` | `metin`, `alt_metin`, `yazi_rengi`, `arkaplan`, `font_boyut`, `efekt` (fade/typewriter/scale/slide-up), `arkaplan_resim` | Text animation with effects. |
| `GECIS_EFFEKTI` | `onceki_metin`, `sonraki_metin`, `arkaplan`, `yazi_rengi`, `gecis_tipi` (slide-left/slide-right/fade/zoom/wipe), `hiz` | Transition between two scenes. |
| `GRAFIK_ANIMASYONU` | `baslik`, `veri` (list), `grafik_tipi` (bar/horizontal-bar/line), `renkler`, `arkaplan`, `baslik_rengi` | Animated bar/line chart. |

**Örnek:**
```python
from reymen.tools.hyperframes_tool import hyperframes_olustur
sonuc = hyperframes_olustur(
    template="METIN_ANIMASYONU",
    params={"metin": "Merhaba Dünya!", "arkaplan": "#1a1a2e", "efekt": "fade"},
    cikti="output.mp4",
    fps=30, sure=5,
)
```

---

## 📓 Obsidian Vault Integration — `reymen.tools.obsidian_tool`

Full Obsidian vault integration: list, read, create, update, search .md files.

**Motor Araçları (6 adet):**
| Araç Adı | Parametreler | Açıklama |
|----------|-------------|----------|
| `OBSIDIAN_LISTE(vault_yolu\|alt_dizin)` | `vault_yolu (ops)`, `alt_dizin (ops)` | List .md files in the vault. |
| `OBSIDIAN_OKU(dosya_yolu\|vault_yolu)` | `dosya_yolu (zrn)`, `vault_yolu (ops)` | Read contents of a .md file. |
| `OBSIDIAN_YAZ(dosya_yolu\|\|icerik)` | `dosya_yolu (zrn)`, `icerik (zrn)` | Create a new .md note. |
| `OBSIDIAN_GUNCELLE(dosya_yolu\|\|icerik\|\|mod)` | `dosya_yolu (zrn)`, `icerik (zrn)`, `mod (ops: overwrite/append/prepend)` | Update an existing .md note. |
| `OBSIDIAN_ARA(sorgu\|vault_yolu\|harf_duyarli)` | `sorgu (zrn)`, `vault_yolu (ops)`, `harf_duyarli (ops: true/false)` | Search vault by keyword / regex. |
| `OBSIDIAN_BILGI(vault_yolu)` | `vault_yolu (ops)` | Show summary info about the vault. |

**Modül Fonksiyonları:**
```python
motor_kaydet(motor) -> None  # Register Obsidian tools with the Motor (6 tools)
```

**Örnek:**
```python
from reymen.tools.obsidian_tool import motor_kaydet
motor_kaydet(motor)  # OBSIDIAN_LISTE, OBSIDIAN_OKU, OBSIDIAN_YAZ, etc.
```

---

## 📜 Kurallar (Rules Engine) — `reymen.sistem.kurallar`

**`RulesEngine(rules_file=None)`** — Policy katmanı. Her aksiyon (dosya, ağ, komut, API) öncesinde kurallar kontrol edilir.

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `kontrol(kategori, hedef, baglam=None)` | `kategori: str`, `hedef: Any`, `baglam: Optional[dict]` | `dict` | Bir aksiyonu kurallara göre kontrol et. Döner: `{"izin": bool, "sebep": str, "kural": str, "tip": str, "kural_id": str}` |
| `toplu_kontrol(kontroller)` | `kontroller: list[dict]` | `list[dict]` | Birden fazla kontrolü tek seferde yap. |
| `kural_ekle(kategori, tip, desen, sebep="", kural_id=None)` | `kategori: str`, `tip: str`, `desen: str`, `sebep: str`, `kural_id: Optional[str]` | `tuple[bool, str]` | Yeni kural ekle. |
| `kural_sil(kural_id)` | `kural_id: str` | `tuple[bool, str]` | Kural sil (builtin korumalı). |
| `kural_guncelle(kural_id, **kwargs)` | `kural_id: str`, `**kwargs` | `tuple[bool, str]` | Kural güncelle (aktif/pasif, sebep vb.). |
| `kural_bul(kural_id)` | `kural_id: str` | `Optional[dict]` | ID'ye göre kural bul. |
| `kural_listele(kategori=None, tip=None, sadece_aktif=False)` | `kategori: Optional[str]`, `tip: Optional[str]`, `sadece_aktif: bool` | `list[dict]` | Kuralları filtreleyerek listele. |
| `kategorileri_listele()` | — | `dict` | Kuralları kategorilere göre grupla. |
| `yeniden_yukle()` | — | `int` | Kuralları yeniden yükle. Kural sayısını döndür. |
| `kural_sayisi` (property) | — | `int` | Toplam kural sayısı. |
| `aktif` (property) | — | `bool` | Kural motoru aktif mi? |

**Kategoriler:** `dosya_erisim`, `ag`, `komut`, `api_cagrisi`, `guvenlik`

**Kural Tipleri:** `izin`, `engel`, `uyari`

**Desen Destekleri:** Tam eşleşme, Wildcard (`**/etc/*`), Regex (`re:...` ön eki ile)

**Örnek:**
```python
from reymen.sistem.kurallar import RulesEngine
engine = RulesEngine()
engine.kural_ekle("dosya_erisim", "engel", "**/.env", sebep="API anahtarları içerir")
sonuc = engine.kontrol("dosya_erisim", "/proje/.env")
# {"izin": False, "sebep": "Engellendi: API anahtarları içerir", ...}
```

---

## 🔐 Auth System — `reymen.guvenlik.reymen_auth`

**`auth_manager` (singleton)** — API key validation, JWT token management, permission levels and multi-user support.

| Fonksiyon | Parameters | Returns | Description |
|-----------|-----------|---------|-------------|
| `validate_api_key(api_key)` | `api_key: str` | `Optional[str]` | API key format doğrulama + provider tespiti. |
| `create_token(username, role="user", expires_in=3600)` | `username: str`, `role: str`, `expires_in: int` | `AccessToken` | JWT token oluştur. |
| `verify_token(access_token)` | `access_token: str` | `Optional[dict]` | Token doğrulama (imza + expiry). |
| `refresh_token(refresh_token)` | `refresh_token: str` | `Optional[AccessToken]` | Token yenileme. |

### `JWTManager(secret_key=None)`

HMAC-SHA256 JWT token management — no external dependencies.

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `encode(payload, expires_in=3600)` | `payload: dict`, `expires_in: int` | `str` | Create JWT token. |
| `decode(token, verify=True)` | `token: str`, `verify: bool` | `Optional[dict]` | Decode and verify JWT token. |
| `refresh_token(token, expires_in=3600)` | `token: str`, `expires_in: int` | `Optional[str]` | Refresh an existing token. |

### `AuthStorage(db_path=None)`

SQLite-backed user and token storage.

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `create_user(username, role="user", email="", password_hash="")` | `username: str`, `role: str`, `email: str`, `password_hash: str` | `User` | Create user. |
| `get_user(user_id)` | `user_id: str` | `Optional[User]` | Get user by ID. |
| `get_user_by_username(username)` | `username: str` | `Optional[User]` | Get user by username. |
| `list_users()` | — | `list[User]` | List all users. |
| `update_user(user_id, **kwargs)` | `user_id: str`, `**kwargs` | `bool` | Update user fields. |
| `delete_user(user_id)` | `user_id: str` | `bool` | Delete user and tokens. |
| `save_token(user_id, access_token, refresh_token, expires_in, role="user", scope="")` | ... | `str` | Save token. |
| `revoke_token(token_id)` | `token_id: str` | `bool` | Revoke token. |

### `detect_api_key_provider(api_key) -> Optional[str]`
Detect which provider an API key belongs to.

**Desteklenen Provider Formatları:** Anthropic (sk-ant-), OpenRouter (sk-or-), DeepSeek (sk-), OpenAI (sk-), xAI/Grok (xai-), Groq (gsk_)

### `AccessToken` (dataclass)
`access_token`, `token_type`, `expires_in`, `refresh_token`, `scope`, `role`, `user_id`, `issued_at`, `is_expired` (property), `expires_at` (property)

### `User` (dataclass)
`user_id`, `username`, `role` (admin/user/guest), `email`, `api_keys`, `is_active`, `created_at`, `last_login`, `metadata`

**Örnek:**
```python
from reymen.guvenlik.reymen_auth import AuthStorage, JWTManager
jwt = JWTManager()
token = jwt.encode({"sub": "kullanici_adi", "role": "admin"})
payload = jwt.decode(token)
```

---

## 🔄 A2A/ACP Protocol — `reymen.a2a_acp`

Agent Communication Protocol (JSON-RPC 2.0 based) server and client. Extends A2A with Agent Card, Skill Transfer, and Task Delegation.

### `ACPServer(host="localhost", port=9200)`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `start()` | — | `None` | Start the ACP server. |
| `stop()` | — | `None` | Stop the ACP server. |
| `register_handler(method, handler)` | `method: str`, `handler: callable` | `None` | Register a JSON-RPC method handler. |

### `ACPClient(endpoint_url)`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `initialize()` | — | `bool` | Initialize connection. |
| `tools_list()` | — | `list[dict]` | List available tools from server. |
| `tool_call(tool_name, args)` | `tool_name: str`, `args: dict` | `Any` | Call a tool on the server. |
| `close()` | — | `None` | Close connection. |

### Veri Modelleri

**`AgentCard(agent_id, name, version, description, capabilities, skills, transport, endpoints, metadata, public_key, last_seen)`**
Agent yetkinlik bildirimi. Agent'ların keşfi ve yetenek paylaşımı için.

| Method | Returns | Description |
|--------|---------|-------------|
| `to_dict()` | `dict` | Serialize to dict. |
| `from_dict(data)` | `AgentCard` | Deserialize from dict. |

**`SkillPackage(skill_id, name, description, content, source_agent, target_agent, version, dependencies, category, tags, signature, transferred_at)`**
Agent'lar arası beceri aktarım formatı.

**`DelegationTask(task_id, source_agent, target_agent, title, description, context, priority, deadline, status, result, error, metadata, created_at, completed_at)`**
Görev devretme paketi.

### `AgentCardRegistry`
Merkezi Agent Card kayıt defteri.

| Method | Returns | Description |
|--------|---------|-------------|
| `register(card)` | `None` | Register or update an Agent Card. |
| `unregister(agent_id)` | `bool` | Remove an Agent Card. |
| `get(agent_id)` | `AgentCard \| None` | Get agent card. |
| `list(capability=None)` | `list[AgentCard]` | List all (or filtered) cards. |
| `search_by_skill(skill_name)` | `list[AgentCard]` | Search agents by skill. |
| `search_by_metadata(key, value)` | `list[AgentCard]` | Search by metadata. |
| `heartbeat(agent_id)` | `bool` | Update last_seen timestamp. |
| `cleanup_stale(max_age=300)` | `int` | Remove stale agents (default: 5 min). |
| `count()` | `int` | Registered agent count. |
| `on_discovery(handler)` | `None` | Add discovery handler. |
| `to_dict()` | `dict` | Full registry as dict. |

**`AgentCapability` enum:** MESSAGING, TOOL_EXECUTION, SKILL_TRANSFER, TASK_DELEGATION, STREAMING, BROADCAST, HEARTBEAT, FILE_TRANSFER

**`ACPErrorCode` (JSON-RPC):** PARSE_ERROR (-32700), METHOD_NOT_FOUND (-32601), TOOL_NOT_FOUND (-32001), SERVER_NOT_INITIALIZED (-32000), etc.

**Örnek:**
```python
from reymen.a2a_acp import ACPServer, ACPClient, AgentCard, AgentCardRegistry

# Sunucu
server = ACPServer()
server.start()

# Agent Card kaydı
registry = AgentCardRegistry()
card = AgentCard(agent_id="agent-001", name="ReYMeN", version="0.9.0",
                 capabilities=["messaging", "tool_execution"])
registry.register(card)

# İstemci
client = ACPClient("http://localhost:9200")
client.initialize()
tools = client.tools_list()
```

---

## 🧩 Framework Adaptörü — `reymen.arac.framework_adaptor`

**`FrameworkYonetici()`** — External AI Framework Adapters for LangGraph, CrewAI, and AutoGen (AG2).

### `LangGraphAdaptor`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `calistir(graph, inputs=None, config=None)` | `graph: StateGraph`, `inputs: Optional[dict]`, `config: Optional[dict]` | `dict` | Run an existing StateGraph. |
| `basit_is_akisi(nodes, inputs=None, state_type=None)` | `nodes: list[Callable]`, `inputs: Optional[dict]`, `state_type: Optional[TypedDict]` | `dict` | Create and run a simple sequential graph. |
| `kullanilabilir_mi()` | — | `bool` | Check if LangGraph is available. |

### `CrewAIAdaptor`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `crew_calistir(crew, inputs=None)` | `crew: Crew`, `inputs: Optional[dict]` | `dict` | Run an existing Crew. |
| `basit_ekip_calistir(agents, tasks, isim="Ekip")` | `agents: list[Agent]`, `tasks: list[Task]`, `isim: str` | `dict` | Create and run a simple crew. |
| `kullanilabilir_mi()` | — | `bool` | Check if CrewAI is available. |

### `AutoGenAdaptor`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `calistir(agent, message)` | `agent: ConversableAgent`, `message: str` | `dict` | Run an AutoGen agent. |
| `iki_ajan_sohbet(agent1, agent2, message, max_turns=10)` | `agent1`, `agent2`, `message: str`, `max_turns: int` | `dict` | Two-agent conversation. |
| `kullanilabilir_mi()` | — | `bool` | Check if AutoGen is available. |

### `framework_adaptor` (Module-level singleton)

```python
framework_adaptor.aktif_frameworkler -> dict[str, bool]  # Which frameworks are installed
framework_adaptor_durum() -> dict  # Status report of all adapters
```

**Örnek:**
```python
from reymen.arac.framework_adaptor import framework_adaptor

# LangGraph workflow
if framework_adaptor.langgraph.kullanilabilir_mi():
    sonuc = framework_adaptor.langgraph.basit_is_akisi(
        nodes=[islev1, islev2],
        inputs={"messages": [{"role": "user", "content": "merhaba"}]}
    )
```

---

## ⚙️ Setup Wizard — `reymen.sistem.setup_wizard`

ReYMeN first setup wizard (`reymen setup`). Hermes' `hermes setup` counterpart.

| Fonksiyon | Returns | Description |
|-----------|---------|-------------|
| `python_kontrol()` | `bool` | Python 3.11+ kontrolü. |
| `git_kontrol()` | `bool` | Git yüklü mü kontrol et. |
| `ffmpeg_kontrol()` | `bool` | FFmpeg yüklü mü. |
| `playwright_kontrol(oto_kur=False)` | `bool` | Playwright yüklü mü, gerekirse kur. |
| `api_key_yapilandirmasi()` | `bool` | API key yapılandırması (DeepSeek öncelikli). |
| `config_kontrol()` | `bool` | config.yaml kontrolü/oluşturma. |
| `soul_kontrol()` | `bool` | SOUL.md kontrolü. |
| `skills_kontrol()` | `bool` | skills/ dizini kontrolü. |
| `setup_calistir(oto_kur=False)` | `int` | Tüm setup'ı çalıştır (exit code). |

**Checklist:** Python 3.11+ → Git → FFmpeg → Playwright → API Keys → config.yaml → SOUL.md → skills/

---

## 🔄 Self-Update — `reymen.sistem.self_update`

Autonomous self-update system. Checks GitHub releases, auto-downloads and installs.

| Fonksiyon | Parameters | Returns | Description |
|-----------|-----------|---------|-------------|
| `check_for_updates()` | — | `dict` | Check GitHub for latest release. `{"guncel_var": bool, "mevcut_versiyon": str, "yeni_versiyon": str, ...}` |
| `perform_update()` | — | `dict` | Perform git pull update. `{"basarili": bool, "cikti": str}` |
| `auto_update_check()` | — | `None` | Automatic weekly check (threaded, silent). |

**Yardımcı Fonksiyonlar:**
```python
_mevcut_versiyon() -> str  # Read current version from pyproject.toml
_versiyon_karsilastir(v1, v2) -> int  # -1: güncelleme gerekli, 0: eşit, 1: mevcut daha yeni
_git_pull() -> dict  # git pull — fetch latest changes
```

---

## 🌙 Nightly Self-Improvement — `reymen.scripts.nightly_improvement`

6-stage silent loop that runs every night at 03:00.

**Aşamalar:**
| Aşama | Fonksiyon | Açıklama |
|-------|-----------|----------|
| 1 | `_asama_once_hafiza()` | once_hafiza analizi (zayıf noktalar) |
| 2 | `_asama_skill_iyilestirme()` | Düşük başarılı skill'leri iyileştir |
| 3 | `_asama_memory_compaction()` | Memory compaction kontrolü |
| 4 | `_asama_kod_kalitesi()` | Code quality (ruff/bandit) |
| 5 | `_asama_cron_durumu()` | Cron job durumu |
| 6 | `_asama_trend_raporu()` | 7-day trend report |

**Çalıştırma:** `python -m reymen.scripts.nightly_improvement`

**`NightlyRapor` (dataclass):** `timestamp`, `asamalar`, `toplam_sure_sn`, `basarili_asama`, `toplam_asama`, `uyari_var`, `trend`, `ozet`

---

## 📏 Skill Shrink — `reymen.scripts.skill_shrink`

Detects bloated skills (10KB+ or 300+ lines), shrinks content, splits sections to references/ subfolder.

**CLI Kullanımı:**
```
reymen skill shrink --dry-run     # detect only
reymen skill shrink --apply       # apply shrinkage
reymen skill shrink --stats       # statistics
```

**Modül Fonksiyonları:**
| Fonksiyon | Parameters | Returns | Description |
|-----------|-----------|---------|-------------|
| `tara_skill_dizini(skills_yolu)` | `skills_yolu: Path` | `list[dict]` | Scan skills directory. |
| `siskinlik_analizi(icerik)` | `icerik: str` | `list[dict]` | Bloat analysis of skill content. |
| `references_bolumleri_bul(icerik)` | `icerik: str` | `list[dict]` | Find sections movable to references/. |

**Şişkinlik Desenleri:** uzun_kod_ornegi, gereksiz_aciklama, asiri_frontmatter, asiri_ornek_liste, tekrar_uyari, asiri_alt_baslik

---

## 🛠️ Browser Tools — `reymen.arac`

### Advanced Browser — `araclar_gelismes.py`
| Method | Description |
|-------|----------|
| `ac(url)` | Open page, read text |
| `screenshot(url, output)` | Screenshot |
| `js_calistir(url, js)` | JavaScript execution |
| `tikla(selector)` | Click |
| `fill(selector, value)` | Form fill |
| `type_text(selector, value)` | Type text |
| `select_option(selector, value)` | Select option |
| `wait_for(selector, timeout)` | Wait for element |
| `wait_for_text(text, timeout)` | Wait for text |
| `hover(selector)` | Hover |
| `scroll(dx, dy)` | Scroll |
| `back() / forward() / reload()` | History |
| `new_tab(url)` / `switch_tab(index)` / `close_tab(index=-1)` | Tab management |
| `tabs_list()` | List tabs |
| `snapshot(max)` / `html(max)` | Content |
| `title()` / `url()` | Page info |
| `dialog_accept()` / `dialog_dismiss()` | Dialogs |
| `network_requests(limit)` | Network |
| `cookies()` / `clear_state()` | State |
| `kapat()` | Close |

### Simple Browser — `araclar_tarayici.py`
| Method | Description |
|-------|----------|
| `sayfa_ac_ve_oku(url, selector)` | Open + read |
| `tikla_ve_yaz(url, click_sel, input_sel, text)` | Click + type |

---

## 📦 Plugin & Tool System — additional modules

| Module | Path | Description |
|--------|------|-------------|
| Tool Registry | `reymen.arac.tool_registry` | `ToolRegistry` — central tool registry |
| Tool Executor | `reymen.arac.tool_executor` | `ToolExecutor` — tool execution engine |
| Plugin Manager | `reymen.sistem.plugin_manager` | `PluginManager` — plugin lifecycle |
| Skill Activator | `reymen.cereyan.skill_activator` | `SkillActivator` — auto-activation from query |
| Skill Library | `reymen.cereyan.skill_library` | SQLite skill library with FTS5 |
| Prompt Builder | `reymen.arac.prompt_builder` | `PromptBuilder` — dynamic prompt assembly |
| Prompt Caching | `reymen.arac.prompt_caching` | `PromptCache` — Anthropic/OpenAI cache control |
| Context Compressor | `reymen.hafiza.context_compressor` | `ContextCompressor` — token-aware compression |
| Once Hafiza | `reymen.sistem.once_hafiza` | `OnceHafiza` — priority memory |
| Delegasyon | `reymen.ag.delegasyon` | `DelegasyonSistemi` — subagent delegation |
| Gateway Manager | `reymen.core.gateway_manager` | Multi-platform gateway management |
| Cron Manager | `reymen.core.cron_manager` | Cron job scheduler + watchdog |
| Schema Manager | `reymen.core.schema_manager` | SQLite schema versioning |
| OAuth Service | `reymen.guvenlik.oauth_servis` | `OAuthServis` — Google/GitHub/Discord OAuth |
| Web Search Engine | `reymen.arac.web_search_engine` | Multi-backend web search |
| Image Gen Engine | `reymen.arac.image_gen_engine` | FAL/OpenAI/xAI image generation |
| Browser Engine | `reymen.arac.browser_engine` | PlaywrightMCP/BrowserUse automation |
| Observability | `reymen.core.observability` | `trace_llm_call`, `trace_tool_call` — LLM/tool tracing |
| Error Classifier | `reymen.cereyan.hata_siniflandirici` | `api_hatasini_siniflandir` — API error classification |
| Message Repair | `reymen.cereyan.mesaj_tamirci` | Tool call argument sanitization, message sequence repair |
| Stream Diagnostics | `reymen.cereyan.stream_diagnostics` | `StreamSaglikTakibi` — stream health monitoring |
| Continuous Learning | `reymen.cereyan.continuous_learning` | Ongoing learning from interactions |
| Adaptif Ogrenme | `reymen.cereyan.adaptif_ogrenme` | Adaptive learning module |
| Iteration Budget | `reymen.cereyan.iteration_budget` | `IterationBudget` — token/turn budgeting |
| Provider Abstraction | `reymen.cereyan.provider_abstraction` | `ProviderBase`, `get_provider` — provider abstraction layer |

---

## 📝 Configuration

### .env Variables

| Variable | Description |
|----------|-------------|
| `DEEPSEEK_API_KEY` | DeepSeek API key |
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `GROQ_API_KEY` | Groq API key |
| `OPENROUTER_API_KEY` | OpenRouter API key |
| `GEMINI_API_KEY` | Google Gemini API key |
| `XAI_API_KEY` | xAI/Grok API key |
| `TOGETHER_API_KEY` | Together AI API key |
| `FIREWORKS_API_KEY` | Fireworks AI API key |
| `MISTRAL_API_KEY` | Mistral AI API key |
| `COHERE_API_KEY` | Cohere API key |
| `PERPLEXITY_API_KEY` | Perplexity API key |
| `REYMEN_JWT_SECRET` | JWT secret key for auth |
| `CONTEXT_ESIK` | Context compression threshold (default: 0.50) |
| `CB_MAX_HATA` | Circuit breaker max errors (default: 3) |
| `CB_SURESI` | Circuit breaker duration (0 = manual) |
| `MAX_RETRY` | Max LLM API retry (default: 3) |
| `DELEGATE_MAX_PARALEL` | Max parallel sub-agents (default: 5) |
| `DELEGATE_TIMEOUT` | Sub-agent timeout (default: 120s) |
| `PROVIDER_LIMIT_*` | Per-provider token limits |
