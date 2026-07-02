# ReYMeN

**Autonomous Task Solver AI Assistant** — A self-improving autonomous system with a multi-provider LLM layer, 100+ tool calling engine, closed learning loop, and A2A messaging.

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11%2B-blue" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License">
  <img src="https://img.shields.io/badge/version-0.9.0-orange" alt="Version 0.9.0">
  <img src="https://img.shields.io/badge/providers-12%2B-purple" alt="12+ Providers">
</p>

---

## 🚀 Quick Links

| | |
|---|---|
| 📖 [Quickstart Guide](kurulum.md) | 🛠️ [CLI Reference](cli.md) |
| 📡 [API Reference](API.md) | 🏗️ [Architecture](mimari.md) |
| ⚙️ [Configuration](configuration.md) | 🤝 [Contributing](CONTRIBUTING.md) |

---

## ✨ Features

### 🧠 Multi-LLM Support
12+ providers including **DeepSeek, OpenAI, Anthropic, Gemini, Groq, Ollama, LM Studio, OpenRouter** — with automatic failover and provider switching mid-conversation.

### 🛠️ 100+ Tools
Built-in tool engine covering **file operations, terminal execution, web search & scrape, browser automation, image generation, video processing, audio TTS/STT, vector memory, and more.**

### 🤝 A2A Messaging
Thread-safe queue-based **inter-agent communication** protocol. Agents can send messages, broadcast, delegate tasks, and coordinate as a swarm.

### 📊 Kanban Board
Full kanban system with **cards, columns, priorities, deadlines, WIP limits, swarm task distribution**, and persistent storage.

### 🔒 Security
**Guardrails, Docker sandbox, PII redaction, OAuth 2.0 authentication, approval workflows** for destructive commands, and path traversal protection.

### 🧩 Plugin System
**Hot-reloadable plugins** with provider plugins, custom tool addition, and MCP/ACP protocol support.

### 💾 Memory & Learning
**Vector memory** (ChromaDB + TF-IDF), **FTS5 full-text search**, **error→solution learning loop**, **semantic cache**, and **context compression**.

### 🌐 Web UI & Desktop
**FastAPI + HTMX management panel** with real-time logs, sandbox, and gateway controls. **Desktop app** with system tray and auto-start.

---

## 📦 Quick Start

```bash
# Clone the repository
git clone https://github.com/recaiozil-wq/reymen-agean.git
cd reymen-agean

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install
pip install -e .

# Run
reymen chat
```

[→ Full Installation Guide](kurulum.md)

---

## 📚 Documentation

| Section | Description |
|---------|-------------|
| [Quickstart](kurulum.md) | Installation and first run |
| [Usage Guide](kullanim.md) | Chat, web, kanban, cron, plugins |
| [CLI Reference](cli.md) | All commands and parameters |
| [API Reference](API.md) | Python API, A2A, MCP, tools |
| [Features](oezellikler.md) | Complete feature list |
| [Architecture](mimari.md) | System design and data flow |
| [Configuration](configuration.md) | Config file and environment variables |
| [Contributing](CONTRIBUTING.md) | Developer guide |
| [Video Guide](video.md) | Setup and usage videos |

---

## 🔧 System Requirements

| Requirement | Detail |
|-------------|--------|
| **Python** | 3.11+ |
| **OS** | Windows 10/11 (native), Linux/macOS |
| **RAM** | 4 GB minimum (8 GB recommended) |
| **Disk** | 500 MB for installation |
| **Internet** | Required for LLM API calls |

---

## 💬 Support

| Channel | Detail |
|---------|--------|
| GitHub Issues | Bug reports and feature requests |
| Telegram | [@Pasa_38](https://t.me/Pasa_38) |
| License | [MIT](LICENSE) |

---

*ReYMeN — Fully independent AI agent. Zero external dependencies for core operation.*
