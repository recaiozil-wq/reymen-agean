<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge&logo=opensourceinitiative&logoColor=white" alt="MIT License">
  <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge" alt="Active Development">
  <img src="https://img.shields.io/badge/Lines-231K-8A2BE2?style=for-the-badge" alt="231K+ Lines">
  <img src="https://img.shields.io/badge/Platforms-17+-blue?style=for-the-badge&logo=telegram&logoColor=white" alt="17+ Platforms">
  <img src="https://img.shields.io/badge/Reasoning-Ornith--1.0-orange?style=for-the-badge" alt="Ornith-1.0">
</p>

<h1 align="center">🚀 ReYMeN</h1>
<h3 align="center">Self-Healing, Multi-Bot Agent Framework with Native Reasoning Core</h3>

<p align="center">
  <b>ReYMeN</b> isn't just another AI agent framework — it's a <b>self-aware</b>, <b>self-healing</b>, <b>multi-platform</b> agent ecosystem. <br>
  Run <b>3 bots</b> from a single center, deploy across <b>17+ platforms</b>, with a <b>closed-loop learning</b> engine that thinks, improves, and repairs itself.
</p>

<p align="center">
  <b>694 Python files · 231K+ lines of code · Single developer · MIT Licensed</b>
</p>

<p align="center">
  <i>Created by <b>Marko (Pasa_38)</b> — <a href="https://t.me/Pasa_38_bot">@Pasa_38_bot</a></i>
</p>

---

## 📋 Table of Contents

- [🔥 ReYMeN vs The World](#-reymen-vs-the-world)
- [🚀 Quickstart (1 Minute)](#-quickstart-1-minute)
- [✨ Key Features](#-key-features)
- [📊 Hermes → ReYMeN Feature Parity](#-hermes--reymen-feature-parity)
- [📂 Directory Structure](#-directory-structure)
- [🎯 Usage Examples](#-usage-examples)
- [🛠 Developer](#-developer)
- [📜 License](#-license)

---

## 🔥 ReYMeN vs The World

| Feature | ReYMeN | LangGraph | CrewAI | AutoGen | OpenAI SDK | Hermes |
|---------|:------:|:---------:|:------:|:-------:|:----------:|:------:|
| **Own Reasoning Core** | ✅ **Ornith-1.0** | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Multi-Bot Single Center** | ✅ **3 shared bots** | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Plugin System (hooks)** | ✅ (7 lifecycle hooks) | ✅ | ✅ | ❌ | ❌ | ✅ |
| **MCP Server** | ✅ (self-hosted, 6 tools) | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Platform Gateways** | ✅ **17+ platforms** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Container Sandbox** | ✅ (Docker isolation) | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Self-Healing** | ✅ **8 proactive checks** | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Provider Abstraction** | ✅ 5+ providers | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Session Search (FTS5)** | ✅ SQLite FTS5 | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Sub-agent Delegation** | ✅ ThreadPoolExecutor | ❌ | ✅ | ✅ | ❌ | ✅ |
| **Memory Compaction** | ✅ (50K limit, auto-archive) | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Rules Engine** | ✅ 5 categories, 6 rules | ❌ | ❌ | ❌ | ❌ | ✅ |
| **A2A / ACP Protocol** | ✅ A2A messaging | ❌ | ❌ | ✅ ACP | ❌ | ✅ ACP |
| **Web UI** | ✅ FastAPI + JWT Auth | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Image / Video Generation** | ⚠️ Partial | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Turkish Language Support** | ✅ **Fully Turkish** | ❌ | ❌ | ❌ | ❌ | ❌ |
| **GitHub Stars** | ⭐ *Yours!* | 12K+ | 25K+ | 35K+ | — | 5K+ |

> **Legend:** ✅ = Full support | ⚠️ = Partial / In progress | ❌ = Not available  
> *Stats for other frameworks are approximate and sourced from public repositories.*

---

## 🚀 Quickstart (1 Minute)

```bash
# 1. Clone
git clone https://github.com/recaiozil-wq/reymen-agent.git
cd reymen-agent

# 2. Virtual environment
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .

# 3. Add your API key
cp config/.env.example .env
# Set DEEPSEEK_API_KEY or OPENAI_API_KEY in .env

# 4. Run
python -c "from src.reymen.cereyan.beyin import Beyin; b = Beyin({'model':{'provider':'deepseek','model':'deepseek-v4-flash'}}); print(b.dusun('Merhaba!'))"
```

Or with Docker:

```bash
cd docker && docker compose up
```

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🧠 **Reasoning Core** | **Ornith-1.0**: Error → `DURUM_OKU()` → solution → `analytics.db`. Closed learning loop that improves over time |
| 👥 **3 Bots, One Center** | `pasa_38`, `ReYMeN`, `kiral38` share config/memory/sessions via **`durum.json`** (single source of truth) |
| 🧩 **Plugin System** | 7 lifecycle hooks: `on_load`, `on_message`, `pre_llm_call`, `post_llm_call`, `on_session_start/end`, `on_unload` |
| 🔗 **MCP Server** | Self-hosted MCP with 6 tools: `list_sessions`, `send_message`, `search_sessions`, `get_session`, `run_code`, `get_status` |
| 🔑 **Provider Abstraction** | 5+ providers: DeepSeek, OpenAI, Anthropic, xAI, OpenRouter. Switch providers in **one line of config** |
| ✅ **Pydantic Validation** | Type-safe tool calls with automatic JSON repair |
| 📊 **OpenTelemetry** | LLM/tool/session spans with token, cost, and latency tracking |
| 🐳 **Container Sandbox** | Docker isolation (off/partial/full) for secure code execution |
| 📎 **@file / @url Reference** | Inline reading via `@file:config/config.yaml` or `@url:https://...` |
| 🔊 **Voice Mode** | Real-time voice conversation (TTS + STT) |
| 🩺 **Self-Healing** | 8 proactive checks: config drift, watchdog, SOUL sync, state.db pruning, weekly reports |
| 🔄 **Auto Startup** | 3 bots start headlessly on reboot (VBS) |
| 🌐 **17+ Platforms** | Telegram, Discord, WhatsApp, Slack, Teams, Matrix, Signal, Mattermost, DingTalk, Feishu, WeCom, Google Chat, Home Assistant, BlueBubbles, QQ Bot, Yuanbao, and more |
| 🗃️ **FTS5 Session Search** | Full-text search across all sessions with auto-logging |
| 🔄 **Self-Update** | `reymen update --check/--auto` for seamless upgrades |
| 📦 **Memory Compaction** | 50K conversation limit with auto-archive and LRU cache cleanup |
| 📜 **Rules Engine** | 5 categories, 6 built-in rules — every action is validated |
| 🏗️ **Sub-agent Delegation** | `ThreadPoolExecutor`-based parallel task execution |
| 🔐 **JWT Auth System** | Multi-user authentication with access + refresh tokens |
| 🔀 **Framework Adapters** | Optional LangGraph / CrewAI / AutoGen compatibility layer |
| 🖼️ **Web UI Image Gen** | GET/POST `/image-gen` endpoint, 5 providers |
| 🔄 **A2A Messaging** | Agent-to-Agent message broker with thread-safe queues |
| 🎮 **CLI / TUI** | Rich terminal interface with status bars, spinners, and progress indicators |

---

## 📊 Hermes → ReYMeN Feature Parity

| # | Feature | Status |
|---|---------|:------:|
| 1 | **Self-update** — `reymen update --check/--auto` | ✅ |
| 2 | **Session Search** — FTS5 full-text search + auto-logging | ✅ |
| 3 | **Sub-agent Delegation** — ThreadPoolExecutor parallel task execution | ✅ |
| 4 | **HyperFrames Video** — HTML → Playwright → FFmpeg pipeline | ✅ |
| 5 | **Memory Compaction** — 50K limit, auto-archive, LRU cache cleanup | ✅ |
| 6 | **Skill Shrink** — 10KB+ skill detection + references/redirection | ✅ |
| 7 | **Obsidian Integration** — 6 tools (list/read/write/update/search/info) | ✅ |
| 8 | **Setup Wizard** — `reymen setup --check/--fix/--auto` (8 steps) | ✅ |
| 9 | **Nightly Self-Improvement** — 6 stages, every night at 03:00 | ✅ |
| 10 | **Auth System** — JWT token + multi-user + API key validation | ✅ |
| 11 | **Web UI Image Gen** — GET/POST `/image-gen`, 5 providers | ✅ |
| 12 | **Framework Adapters** — LangGraph / CrewAI / AutoGen (optional) | ✅ |
| 13 | **A2A / ACP Protocols** — Agent Card + Skill Transfer + Task Delegation | ✅ |
| 14 | **Rules Engine** — 5 categories, 6 built-in rules, every action checked | ✅ |
| 15 | **Hermes Skills** — 8 new Hermes skills transferred (531 total) | ✅ |

---

## 📂 Directory Structure

```
src/
├── reymen/                  # Framework core
│   ├── cereyan/            # Brain, Motor, Conversation Loop
│   │   ├── beyin.py        # 🧠 Reasoning engine
│   │   ├── motor.py        # ⚙️ Action executor
│   │   ├── conversation_loop.py  # 🔄 Bot conversation loop
│   │   ├── session_search.py     # 🔍 FTS5 search
│   │   ├── memory_compaction.py  # 💾 Memory management
│   │   ├── once_hafiza.py        # 🧠 Confidence-based learning
│   │   └── proaktif_kontrol.py   # 🩺 Proactive maintenance
│   ├── arac/               # Tools (50+)
│   │   ├── tool_registry.py
│   │   ├── tool_executor.py
│   │   └── framework_adaptor.py
│   ├── plugin/             # PluginBase + PluginManager
│   ├── plugins/            # User plugins
│   ├── hafiza/             # Session DB, OnceHafiza, Vector Memory
│   ├── guvenlik/           # Container Sandbox, File Safety, Auth
│   ├── sistem/             # Credential Persistence, DB Config
│   ├── web_ui/             # FastAPI web interface
│   └── tools/              # Obsidian, HyperFrames, Delegation
├── gateways/               # Platform integrations
│   ├── discord_bot.py
│   ├── telegram_bot.py
│   ├── mcp_server.py
│   └── platforms/          # 17+ platform adapters
├── core/                   # Reasoning Core, Credential Pool
│   ├── observability.py
│   ├── credential_pool.py
│   └── provider_abstraction.py
examples/                   # 4 usage scenarios
tests/                      # 112 test files
```

---

## 🎯 Usage Examples

```bash
# Example 1: Hello ReYMeN
python examples/00_merhaba_reymen.py

# Example 2: Write a plugin
python examples/01_plugin_kullanimi.py

# Example 3: Start MCP Server
python -c "from src.gateways.mcp_server import main; main()"

# Example 4: Container Sandbox
python examples/03_container_sandbox.py

# Example 5: One-shot question
python reymen_launcher.py -z "Merhaba, nasılsın?"

# Example 6: Interactive REPL
reymen\bin\reymen.cmd
```

---

## 🏗️ Architecture Highlights

```
┌─────────────────────────────────────────────────────────────┐
│                    🧠 Beyin (Brain)                         │
│           Ornith-1.0 Reasoning Engine                       │
│  Multi-Provider: DeepSeek · OpenAI · Anthropic · xAI · ... │
└──────────────┬──────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────┐
│              ⚙️ Motor (Action Executor)                      │
│     Tool Registry · Tool Executor · Plugin Manager          │
└──────────────┬──────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────┐
│            🔄 Conversation Loop                              │
│     Session DB · Memory Compaction · FTS5 Search            │
└──────┬────────────────────────────────────────────────┬─────┘
       │                                                │
┌──────▼──────┐  ┌──────────▼────────┐  ┌──────────────▼──────┐
│  🌐 Gateway   │  │  🐳 Sandbox      │  │  🖥️ Web UI         │
│  17+ Platforms│  │  Docker Isolate  │  │  FastAPI + JWT     │
│  TG/Discord/..│  │  Code Execution  │  │  Image Gen · Auth  │
└──────────────┘  └───────────────────┘  └─────────────────────┘
```

---

## 🛠 Developer

**Marko (Pasa_38)** — [@Pasa_38_bot](https://t.me/Pasa_38_bot)

- **694 Python files** · **231K+ lines of code**
- Single developer project since inception
- Active daily development with continuous improvement
- Fully independent agent — **zero external framework dependencies**

---

## 📜 License

**MIT License** — use, modify, distribute freely. See [LICENSE](LICENSE) for full terms.

---

<p align="center">
  <b>⭐ Star this repo if you find ReYMeN useful!</b><br>
  <i>Built with ❤️ and Turkish coffee ☕</i>
</p>
