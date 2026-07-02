# ⚙️ Configuration

> ReYMeN is configured via `config/config.yaml` in the project root.

---

## 📁 Configuration File

```yaml
# config/config.yaml
general:
  name: ReYMeN
  version: 0.9.0
  debug: false

model:
  provider: deepseek
  model: deepseek-chat
  temperature: 0.7
  max_tokens: 4096

providers:
  deepseek:
    api_key: ${DEEPSEEK_API_KEY}
    base_url: https://api.deepseek.com
  openai:
    api_key: ${OPENAI_API_KEY}
    base_url: https://api.openai.com/v1
  anthropic:
    api_key: ${ANTHROPIC_API_KEY}
    base_url: https://api.anthropic.com

memory:
  vector_db: chromadb
  session_ttl_days: 30
  max_context_tokens: 32000

web_ui:
  host: 0.0.0.0
  port: 5000
  jwt_secret: ${JWT_SECRET}

logging:
  level: INFO
  file: logs/reymen.log
```

---

## 🔐 Environment Variables (.env)

| Variable | Required | Description |
|----------|----------|-------------|
| `DEEPSEEK_API_KEY` | Recommended | Primary LLM provider |
| `OPENAI_API_KEY` | Optional | OpenAI provider |
| `ANTHROPIC_API_KEY` | Optional | Anthropic/Claude provider |
| `TELEGRAM_BOT_TOKEN` | Optional | Telegram bot integration |
| `JWT_SECRET` | Optional | Web UI authentication |

---

## 🛠️ CLI Configuration Commands

```bash
# View current config
reymen config show

# Set a config value
reymen config set model.provider openai
reymen config set model.temperature 0.5

# Edit config file directly
reymen config edit
```

---

## 🌐 Provider Configuration

ReYMeN supports **12+ LLM providers** with automatic failover:

| Provider | Env Variable | Default Model |
|----------|-------------|---------------|
| DeepSeek | `DEEPSEEK_API_KEY` | deepseek-chat |
| OpenAI | `OPENAI_API_KEY` | gpt-4o |
| Anthropic | `ANTHROPIC_API_KEY` | claude-sonnet-4-20250514 |
| Gemini | `GEMINI_API_KEY` | gemini-2.0-flash |
| Groq | `GROQ_API_KEY` | llama-3.3-70b |
| Ollama | — | llama3 (localhost:11434) |
| LM Studio | — | localhost:1234 |
| OpenRouter | `OPENROUTER_API_KEY` | auto |

---

## 🧩 Plugin Configuration

Plugins live in `reymen/plugins/` and are configured via `plugin.yaml`:

```yaml
# reymen/plugins/my-plugin/plugin.yaml
name: my-plugin
version: 1.0.0
enabled: true
config:
  api_key: ${MY_PLUGIN_API_KEY}
```

Enable/disable plugins:

```bash
reymen plugin enable my-plugin
reymen plugin disable my-plugin
reymen plugin list
```

---

## 🤖 Bot Configuration

Telegram bots and other gateway bots are configured in `.env` and auto-registered in `durum.json`:

```bash
# .env
TELEGRAM_BOT_TOKEN=your_bot_token_here
```
