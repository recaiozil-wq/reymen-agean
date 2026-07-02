# ReYMeN

> **A Self-Healing, Multi-Bot Agent Framework with Native Reasoning Core**

LangGraph'ın karmaşıklığına veya CrewAI'nin kısıtlamalarına takılmadan; tek bir merkezden (`durum.json`) 3 farklı botu asenkron yöneten, kendi hatalarından öğrenen ve MCP destekli otonom bir altyapı.

**694 Python dosyası, 231K satır kod, tek geliştirici. MIT lisansı.**

---

## 🔥 ReYMeN vs Dünya

| Özellik | ReYMeN | LangGraph | CrewAI | OpenAI SDK |
|---------|:------:|:---------:|:------:|:----------:|
| Kendi Reasoning Core | ✅ **Ornith-1.0** | ❌ | ❌ | ❌ |
| Multi-Bot Tek Merkez | ✅ **3 bot ortak** | ❌ | ❌ | ❌ |
| Plugin Sistemi (7 hook) | ✅ | ❌ | ❌ | ❌ |
| MCP Server (kendisi sunar) | ✅ | ❌ | ❌ | ❌ |
| Discord + Telegram Gateway | ✅ | ❌ | ❌ | ❌ |
| Container Sandbox | ✅ | ❌ | ❌ | ❌ |
| Proaktif Bakım (8 önlem) | ✅ **ÖZGÜN** | ❌ | ❌ | ❌ |
| Provider Abstraction | ✅ 5 provider | ✅ | ✅ | ✅ |
| Platform Sayısı | 3 (TG/Discord/WA) | ❌ | ❌ | ❌ |

---

## 🚀 Quickstart (1 Dakika)

```bash
# 1. Klonla
git clone https://github.com/recaiozil-wq/reymen-agent.git
cd reymen-agent

# 2. Sanal ortam
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .

# 3. API key'ini ekle
cp .env.example .env
# .env'ye DEEPSEEK_API_KEY veya OPENAI_API_KEY yaz

# 4. Çalıştır
python -c "from src.reymen.cereyan.beyin import Beyin; b = Beyin({'model':{'provider':'deepseek','model':'deepseek-v4-flash'}}); print(b.dusun('Merhaba!'))"
```

Veya Docker ile:
```bash
docker compose up
```

---

## 📂 Dizin Yapısı

```
src/
├── reymen/          # Framework çekirdeği
│   ├── cereyan/     # Beyin, Motor, Conversation Loop
│   ├── arac/        # Tools (50+ araç)
│   ├── plugin/      # PluginBase + PluginManager
│   ├── plugins/     # Kullanıcı eklentileri
│   ├── hafiza/      # Session DB, OnceHafiza, Vector Memory
│   ├── guvenlik/    # Container Sandbox, File Safety
│   └── sistem/      # Credential Persistence, DB Config
├── gateways/        # Platform entegrasyonları
│   ├── discord_bot.py
│   ├── telegram_bot.py
│   ├── mcp_server.py
│   └── platforms/   # WhatsApp, Telegram network
├── core/            # Reasoning Core, Credential Pool
│   ├── observability.py
│   ├── credential_pool.py
│   └── provider_abstraction.py
examples/            # 4 kullanım senaryosu
tests/               # 112 test dosyası
```

---

## ✨ Öne Çıkan Özellikler

| Özellik | Açıklama |
|---------|----------|
| 🧠 **Reasoning Core** | Ornith-1.0 ile hata → DURUM_OKU() → çözüm → analitik.db. Kapalı öğrenme döngüsü |
| 👥 **3 Bot Tek Merkez** | pasa_38, ReYMeN, kiral38 aynı config/hafıza/session. `durum.json` TEK KAYNAK |
| 🧩 **Plugin Sistemi** | 7 lifecycle hook: on_load, on_message, pre_llm_call, post_llm_call, on_session_start/end, on_unload |
| 🔗 **MCP Server** | Kendisi MCP sunar: 6 araç (list_sessions, send_message, search_sessions...) |
| 🔑 **Provider Abstraction** | 5 provider: DeepSeek, OpenAI, Anthropic, xAI, OpenRouter. Tek satırda değiştir |
| ✅ **Pydantic Validation** | Tool çağrılarında type-safe validation, JSON auto-fix |
| 📊 **OpenTelemetry** | LLM/tool/session span'leri, token/maliyet/latency takibi |
| 🐳 **Container Sandbox** | Docker izolasyon (kapali/kismi/tam). Güvenli kod çalıştırma |
| 📎 **@file/@url Referans** | `@file:config.yaml` veya `@url:https://...` ile inline okuma |
| 🔊 **Voice Mode** | Gerçek zamanlı sesli konuşma (TTS + STT) |
| 🩺 **Proaktif Bakım** | 8 önlem: config drift, watchdog, SOUL sync, state.db prune, haftalık rapor |
| 🔄 **Otomatik Startup** | Reboot'ta 3 bot penceresiz başlar (VBS) |

---

## 🎯 Kullanım Senaryoları

```bash
# Örnek 1: Merhaba ReYMeN
python examples/00_merhaba_reymen.py

# Örnek 2: Plugin yazma
python examples/01_plugin_kullanimi.py

# Örnek 3: MCP Server başlatma
python -c "from src.gateways.mcp_server import main; main()"

# Örnek 4: Container Sandbox
python examples/03_container_sandbox.py
```

---

## 🛠 Geliştirici

Tek geliştirici: **Marko (Pasa_38)** — [@Pasa_38_bot](https://t.me/Pasa_38_bot)

---

## 📜 Lisans

MIT License — dilediğiniz gibi kullanın, değiştirin, dağıtın.
