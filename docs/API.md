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

## 🤝 A2A Messaging — `reymen.a2a`

Thread-safe queue-based inter-agent messaging protocol.

### Classes

#### `MessageType(str, Enum)`
Message types: `TEXT`, `TASK`, `RESULT`, `QUERY`, `RESPONSE`, `ERROR`, `BROADCAST`, `HEARTBEAT`

#### `Message(sender, receiver, content, type=TEXT, id=uuid, reply_to=None, timestamp, metadata={})`
A2A message data structure.

| Method | Returns | Description |
|-------|---------|----------|
| `as_dict()` | `dict` | Convert message to dictionary |
| `reply(content, msg_type=None)` | `Message` | Create reply message (sender↔receiver swapped) |

#### `Broker()`
Central message broker. Thread-safe.

| Method | Returns | Description |
|-------|---------|----------|
| `register(agent_id)` | `None` | Register agent |
| `unregister(agent_id)` | `None` | Remove agent registration |
| `is_registered(agent_id)` | `bool` | Check if registered |
| `send(message)` | `None` | Send message (throws `A2AError` if target not registered) |
| `broadcast(sender, content, exclude=None)` | `list[str]` | Broadcast to all agents |
| `receive(agent_id, timeout=None, block=True)` | `Message\|None` | Receive message |
| `peek(agent_id)` | `Message\|None` | Peek without consuming |
| `inbox_size(agent_id)` | `int` | Number of pending messages |
| `set_handler(agent_id, handler)` | `None` | Set message handler |
| `clear_handler(agent_id)` | `None` | Clear handler |
| `message_log()` | `list[Message]` | All delivered messages |
| `stats()` | `dict` | Broker statistics |
| `reset()` | `None` | Clear all inboxes and log |

#### `Agent(agent_id, broker, on_message=None)`
A2A agent. Auto-registers with broker on creation.

| Method | Returns | Description |
|-------|---------|----------|
| `send(receiver, content, msg_type=TEXT, reply_to=None, metadata=None)` | `Message` | Send message |
| `broadcast(content, exclude=None)` | `list[str]` | Broadcast to all agents |
| `reply(original, content)` | `Message` | Reply to message |
| `receive(timeout=None, block=True)` | `Message\|None` | Receive message |
| `peek()` | `Message\|None` | Peek without consuming |
| `inbox_size` | `int` (property) | Number of pending messages |
| `set_handler(handler)` | `None` | Set message handler |
| `clear_handler()` | `None` | Clear handler |
| `close()` | `None` | Unregister from broker |

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

## 🧠 LLM Layer — `reymen.cereyan.beyin`

**`Beyin`** — Multi-provider LLM connection layer. 12+ providers, automatic failover.

| Method | Description |
|-------|----------|
| `dusun(messages, tools=None, stream=False)` | Query LLM |
| `iptal_et()` | Cancel current request |
| `sifirla()` | Reset rate-limit state |
| `dusun_stream(messages, tools=None)` | Streaming query |

**Supported Providers:** LM Studio, DeepSeek, OpenAI, Anthropic, Groq, Azure, Bedrock, Gemini, Moonshot, Ollama, OpenRouter, xAI

---

## 🔄 Conversation Loop — `reymen.cereyan.conversation_loop`

### `GorevCozucu(motor=None, beyin=None, max_turns=30)`

Intelligent task solving with 7-source ensemble comparison.

| Method | Description |
|-------|----------|
| `coz(goal, context=None)` | Simple API (legacy) |
| `run_conversation(goal, context=None, provider=None)` | Advanced API (ReYMeN pipeline) |

**Flow:** QUERY → OnceHafiza → Session search → Skill scan → Ensemble (7 sources) → Save → Response

---

## 🎯 Action Engine — `reymen.cereyan.motor`

### `Motor(backend_mode="local", hafiza_collection=None, config=None)`

Captures actions from LLM output, routes through ToolRegistry + plugins.

| Method | Description |
|-------|----------|
| `hook_kaydet(event, fn)` | Register motor hook |
| `calistir(tool, raw_param)` | Execute tool |
| `calistir_fc(tool, args)` | Execute in function-calling format |
| `tools_schema_al(max=64)` | Generate OpenAI-compatible tool schema |
| `tum_arac_tanimini_al()` | Return all tool definitions |
| `gorev_coz(task_path)` | Resolve task file |
| `eylemi_ayristir(llm_output)` | Extract action name+param from LLM output |
| `musait_araclar(toolset=None)` | List available tools |

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

### `MessageBroker`
queue.Queue-based, thread-safe, 18 message types.

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

`detect()` — Detect platform, `translate_path()`, `run()`, `is_wsl_available()`, `list_wsl_distros()`

---

## 🔄 Self-Improvement — `reymen.self_improve`

### `SelfImprover`

Quality metrics, trend analysis, and automatic improvement.

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
| `motor.py` | Action engine (1,950 lines) |

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
