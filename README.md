# ReYMeN — Otonom Uygulama Otomasyonu Ajanı (v2.0)

Kendi kendine düşünen (ReAct döngüsü), araç kullanan, **hatalardan öğrenen**
ve kendi kendini düzelten otonom yazılım ajanı.
Windows otomasyonunda uzmanlaşmıştır.

## Özellikler

### 🤖 Temel
- **ReAct Döngüsü**: Planla → Düşün → Eylem → Gözlemle → Öğren
- **17+ LLM Provider**: LM Studio, DeepSeek, OpenAI, Anthropic, Groq, Together, Ollama, vb.
- **105+ Araç**: Dosya, shell, Python, web, tarayıcı, ekran OCR, makro, ses, görsel
- **11 Platform**: Telegram, Discord, Signal, WhatsApp, Slack, Matrix, Email, SMS, Webhook
- **10,000+ Test**: 1,842 test dosyası

### 🧠 Otonom Görev Çözücü (YENİ)
- **Model Adapter**: 7 provider (Ollama, LM Studio, GLM, DeepSeek, OpenAI, Anthropic, Gemini) — auto-detect
- **Orchestrator**: `solve_step()` ile adım adım çözüm, 3 retry, JSONL log
- **Öğrenme Döngüsü**: Hata al → hafızada ara (varsa direkt çöz, 0 LLM) → yoksa LLM'e sor → doğrula → kaydet
- **SQLite Hafıza**: `reymen/memory/hafiza.db` — TTL=30gün (basari_sayisi>=3 muaf), soyut imza (SHA256), WAL mode
- **Doğrulamalı Kayıt**: LLM fix'i çalışıyorsa hafızaya kaydet, çalışmıyorsa başarısız etiketiyle kaydet
- **Motor Entegrasyonu**: `motor.script_calistir()`, `motor.ogren()`, `motor.gorev_coz()`

### 🔌 MCP Server Host (YENİ)
- Stdio ve HTTP (SSE) transport
- Diğer MCP client'ları (Claude Code, Cursor) ReYMeN tool'larını çağırabilir
- `python -m reymen.core.mcp_server --transport http --port 9000`

### 🔍 Session Search FTS5 (YENİ)
- `session.db` içinde FTS5 ile tam metin arama
- `session_ara("hata düzeltme", limit=10)` — geçmiş konuşmalarda anında arama

### 🪟 Windows Otomasyonu
- **Tor otomasyonu**: Tor üzerinden form doldurma, login, kayıt, sipariş
- **Hata watchdog + OCR**: Hata yakala, OCR ile oku, otomatik çözüm uygula
- **Nişan/sh template**: 3 aşamalı ekran şablonu bulma (DOM → OpenCV → OCR)
- **Otonom nişan oluşturma**: DOM'dan otomatik şablon çıkarma

### 🐳 Docker (YENİ)
- `docker build -t reymen .` ile container
- `docker-compose up` ile tek komutta ayağa kaldır

### 🧰 Skill Import (YENİ)
- Hermes skill'lerini ReYMeN formatına dönüştür
- `python reymen/scripts/skill_import.py`

## Hızlı Başlangıç

```bash
# 1. Ortamı kur
python -m venv venv
venv\Scripts\pip install -e ".[dev]"

# 2. .env dosyasını düzenle
copy .env.example .env
notepad .env

# 3. ReYMeN'i çalıştır
python main.py
# veya
reymen
```

## Test

```bash
# Tüm testleri çalıştır
pytest tests/ --ignore=tests/ReYMeN_reference

# Coverage ile
pytest tests/ --cov=reymen --cov-report=term-missing

# Paralel test
pytest tests/ -n auto --ignore=tests/ReYMeN_reference
```

## Proje Yapısı

```
ReYMeN-Ajan/
├── reymen/                  # Ana kod paketi
│   ├── core/                # Core (YENİ)
│   │   ├── model_adapter.py # 7 provider, auto-detect
│   │   ├── ogrenme.py       # SQLite hafıza + TTL + öğrenme döngüsü
│   │   ├── orchestrator.py  # solve_step, coz_hata
│   │   ├── mcp_server.py    # MCP server host (HTTP + Stdio)
│   │   └── session_search.py# FTS5 session arama
│   ├── cereyan/             # Motor, ClosedLearningLoop
│   ├── sistem/              # CLI, MCP, cron_scheduler
│   ├── reymen_cli/          # CLI alt komutları
│   ├── scripts/             # Fix/analiz script'leri
│   ├── hafiza/              # Hafıza katmanı
│   ├── guvenlik/            # Güvenlik denetim
│   └── ag/                  # Ağ katmanı
├── agent/                   # Agent katmanı
├── gateway/                 # Telegram gateway
├── tools/                   # Araç sistemi (105+ araç)
├── plugins/                 # Plugin sistemi
├── tests/                   # Testler
├── desktop/                 # Electron masaüstü
├── docs/mimari/             # Mimari dokümanlar (HTML)
├── .ReYMeN/                 # Proje metadata
├── Dockerfile               # Container (YENİ)
├── docker-compose.yml       # Container orchestration (YENİ)
└── pyproject.toml            # Paket yapılandırması
```

## Geliştirme

```bash
# Kurulum (geliştirme modu)
pip install -e ".[dev]"

# Lint
ruff check reymen/ tools/ agent/

# Güvenlik taraması
bandit -r reymen/ -ll --skip B101,B603

# Proje analizi
python reymen_analiz.py .

# Otonom görev çözücü
python -c "from reymen.cereyan.motor import Motor; m = Motor(); m.script_calistir('reymen/scripts/step_01.py')"
```

## ReYMeN vs Hermes

| Özellik | Hermes | ReYMeN |
|---------|:------:|:------:|
| Web UI | ✅ | ⚠️ dashboard/ var |
| Docker | ✅ | ✅ |
| CI/CD | ✅ | ✅ |
| Model Adapter (7 provider) | ❌ | ✅ |
| Otonom Görev Çözücü | ❌ | ✅ |
| Öğrenme Döngüsü (SQLite+TTL) | ❌ | ✅ |
| MCP Server Host | ✅ | ✅ |
| Session Search FTS5 | ✅ | ✅ |
| Tor otomasyonu | ❌ | ✅ |
| Hata watchdog | ❌ | ✅ |
| Windows OCR | ❌ | ✅ |
| Kapalı öğrenme | ❌ | ✅ |

## Lisans

MIT
