# 🤖 ReYMeN — Otonom Görev Çözücü

**Türkçe yapay zeka asistanı.** Çoklu-provider LLM katmanı, araç çağrı motoru, kapalı öğrenme döngüsü ve A2A mesajlaşma ile kendi kendini geliştiren otonom bir sistem.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-0.9.0-orange)

---

## 📦 Özellikler

| Özellik | Açıklama |
|---------|----------|
| 🧠 **Çoklu LLM** | DeepSeek, OpenAI, Anthropic, Gemini, Groq, LM Studio, Ollama, OpenRouter — 12+ provider |
| 🛠️ **Araç Çağrı Sistemi** | 100+ araç: dosya, terminal, web, tarayıcı, görsel, video, ses |
| 🔄 **A2A Mesajlaşma** | Agent'lar arası thread-safe kuyruk tabanlı iletişim |
| 🧩 **Hook Sistemi** | 8 olay tipi (session/tur/araç/hata/context) |
| 📊 **Kanban** | Kart/kolon/öncelik/deadline yönetimi, WIP limit |
| 💰 **Cost Tracking** | SQLite tabanlı API harcama takibi |
| 🎬 **Video Araçları** | yt-dlp + ffmpeg wrapper |
| 🌐 **Web UI** | FastAPI + HTMX yönetim paneli |
| 🔐 **Güvenlik** | Guardrails, sandbox, PII redaction, path doğrulama |
| 🧠 **Hafıza** | OnceHafıza (vektör), FTS5 session search, context compression |
| 📈 **Self-Improvement** | Kalite metrikleri, trend analizi, otomatik iyileştirme |

---

## 🏗️ Mimari

```
reymen/
├── a2a.py                  # A2A mesajlaşma (Broker + Agent)
├── cli.py                  # Görev 7 CLI
├── cost_tracker.py         # API harcama takibi
├── kanban.py               # Kanban Board + Worker
├── platform_adapter.py     # WSL/Kali path çevirici
├── self_improve.py         # Kalite metrikleri
├── tui.py                  # Rich TUI (status bar, spinner)
├── video_tools.py          # yt-dlp + ffmpeg
├── web_ui.py               # FastAPI web paneli
│
├── ag/                     # Gateway & ACP
├── arac/                   # Araç katmanı (100+ araç)
├── cereyan/                # Ana işlem katmanı
│   ├── conversation_loop.py    # Konuşma döngüsü
│   ├── motor.py                # Eylem motoru
│   ├── beyin.py                # LLM bağlantı katmanı
│   ├── hook_dispatcher.py      # Olay/hook sistemi
│   ├── broker.py               # Mesaj broker
│   └── closed_learning_loop.py # Kapalı öğrenme döngüsü
├── core/                   # Çekirdek modüller
│   ├── model_adapter.py    # Model adapter (Ollama, OpenAI, Anthropic)
│   ├── orchestrator.py     # Görev orkestratörü
│   ├── ogrenme.py          # Hata→çözüm hafızası
│   ├── mcp_server.py       # MCP sunucusu
│   └── session_search.py   # FTS5 session arama
├── guvenlik/               # Güvenlik katmanı
├── hafiza/                 # Hafıza katmanı
├── sistem/                 # CLI, agent lifecycle, sistem yönetimi
└── windows/                # Windows otomasyon araçları
```

---

## 🚀 Kurulum

### Gereksinimler

- Python 3.11+
- pip / venv

### Adımlar

```bash
# 1. Depoyu klonla
git clone https://github.com/Q/reymen.git
cd reymen

# 2. Sanal ortam oluştur
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya Windows: venv\Scripts\activate

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. Playwright (tarayıcı otomasyonu için)
pip install playwright
playwright install chromium

# 5. Ortam değişkenlerini ayarla
cp .env.example .env
# .env dosyasını düzenle: API key'lerini gir
```

### Ortam Değişkenleri

| Değişken | Zorunlu | Açıklama |
|----------|---------|----------|
| `DEEPSEEK_API_KEY` | Evet | DeepSeek API anahtarı |
| `OPENAI_API_KEY` | Hayır | OpenAI API anahtarı |
| `ANTHROPIC_API_KEY` | Hayır | Anthropic Claude API anahtarı |
| `REYMEN_MODEL` | Hayır | Varsayılan model (deepseek-v4-flash) |
| `FAL_KEY` | Hayır | FAL.ai görsel oluşturma |
| `CONTEXT_ESIK` | Hayır | Context sıkıştırma eşiği (0.50) |

---

## 🎮 Kullanım

### CLI Modu

```bash
# Interaktif CLI başlat
python -m reymen

# Durum kontrolü
python -m reymen status

# Maliyet görüntüle
python -m reymen cost

# Kalite raporu
python -m reymen quality

# Kanban yönetimi
python -m reymen kanban

# Video indirme
python -m reymen video download <url>

# A2A mesajlaşma testi
python -m reymen a2a
```

### Python API

```python
from reymen.a2a import Broker, Agent, Message

broker = Broker()
alice = Agent("alice", broker)
bob = Agent("bob", broker)

alice.send("bob", "Merhaba!")
msg = bob.receive()
print(msg.content)  # Merhaba!
```

### Web UI

```bash
python -m reymen web
# http://localhost:8080 adresinde açılır
```

---

## 🧩 Araç Kataloğu

| Kategori | Araçlar |
|----------|---------|
| 🌐 **Tarayıcı** | BROWSER_HEADLESS, BROWSER_FILL, BROWSER_CLICK, BROWSER_WAIT, BROWSER_SELECT, BROWSER_SNAPSHOT, BROWSER_HTML, BROWSER_SCROLL, BROWSER_TABS, BROWSER_NEW_TAB, BROWSER_BACK/FORWARD, BROWSER_HOVER |
| 📁 **Dosya** | DOSYA_OKU, DOSYA_YAZ, DOSYA_SIL, DOSYA_KOPYALA, DOSYA_TAŞI |
| 💻 **Terminal** | KOMUT_CALISTIR, PYTHON_CALISTIR, SHELL_SCRIPT |
| 🌍 **Web** | WEB_ARA, WEB_EXTRACT, SCREEN_SCRAPE |
| 🖼️ **Görsel** | RESIM_OLUSTUR (FAL), VISION_ANALIZ, EKRAN_GORUNTUSU |
| 🎵 **Ses** | SES_KAYDET, SES_OKU, TTS_SOYLE |
| 🎬 **Video** | VIDEO_INDIR, VIDEO_DONUSTUR, VIDEO_KES, SES_CIKAR |
| 📊 **Kanban** | KART_OLUSTUR, KART_LISTELE, KART_TAMAMLA, KART_ENGELLE |
| 🔐 **Güvenlik** | ONAY_ISTE, GUVENLI_KONTROL, PII_TEMIZLE |
| 🔄 **Sistem** | SUPERVISOR_RAPOR, HATA_COZ, OGREN, DURUM |

---

## 🔌 Entegrasyonlar

| Servis | Tür | Açıklama |
|--------|-----|----------|
| **DeepSeek** | LLM | Varsayılan model sağlayıcı |
| **OpenAI** | LLM | GPT-4o / GPT-4o-mini |
| **Anthropic** | LLM | Claude 3.5 Sonnet / Haiku |
| **Google Gemini** | LLM | Gemini 1.5 Pro / Flash |
| **LM Studio** | Lokal LLM | Localhost API |
| **Ollama** | Lokal LLM | Localhost API |
| **OpenRouter** | LLM | Çoklu model yönlendirme |
| **FAL.ai** | Görsel | Resim oluşturma + vision |
| **yt-dlp** | Video | Video indirme |
| **ffmpeg** | Medya | Dönüştürme/kırpma |
| **Playwright** | Tarayıcı | Headless browser otomasyonu |
| **MCP** | Protokol | Model Context Protocol sunucusu |

---

## 🧪 Test

```bash
# Tüm testler
python -m pytest tests/

# Belirli modül
python -m pytest tests/test_a2a.py -v
python -m pytest tests/test_hook_dispatcher.py -v

# Coverage
python -m pytest --cov=reymen tests/
```

---

## 📚 Dokümantasyon

- [API Referansı](docs/API.md) — Modül ve sınıf dokümantasyonu
- [Değişiklik Günlüğü](CHANGELOG.md)
- [Katkı Rehberi](CONTRIBUTING.md)

---

## 🛣️ Yol Haritası

- [x] Çoklu LLM provider desteği
- [x] Araç çağrı sistemi (100+ araç)
- [x] A2A mesajlaşma prototipi
- [x] Hook/olay sistemi
- [x] Kanban board
- [x] Web UI
- [x] MCP Server
- [x] Hata→çözüm öğrenme
- [x] Tarayıcı otomasyonu
- [ ] Çoklu agent orchestration
- [ ] Dağıtık A2A (HTTP transport)
- [ ] Görsel hafıza (multimodal log)
- [ ] Eklenti/plugin marketi

---

## ⚖️ Lisans

MIT License — bakınız [LICENSE](LICENSE)

---

## 🤝 Katkı

Pull request'ler açıktır. Büyük değişikliklerden önce lütfen issue açın.

```bash
# Geliştirme kurulumu
pip install -r requirements-dev.txt
pre-commit install
```
