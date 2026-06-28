<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="MIT">
  <img src="https://img.shields.io/badge/Windows-10%2B-0078D6?logo=windows" alt="Windows">
  <img src="https://img.shields.io/badge/Platform-CLI%20%7C%20Telegram%20%7C%20Web-blueviolet" alt="Platform">
  <img src="https://img.shields.io/badge/Test%20Status-137%20passed-brightgreen" alt="Tests">
</p>

<h1 align="center">🧠 ReYMeN — Otonom Yapay Zeka Ajanı</h1>
<p align="center">
  <b>Türkçe | Açık Kaynak | Windows Odaklı</b><br>
  Kendi kendine öğrenen, araç kullanan, hatalardan ders çıkaran otonom yazılım ajanı.
</p>

---

## 🚀 Nedir?

**ReYMeN**, yapay zeka asistanlarını tek bir merkezden yönetmek için geliştirilmiş **açık kaynak bir platformdur.** Hermes Agent tabanlıdır, Türkçe dil desteği ile Windows odaklı çalışır.

Telegram botları, CLI, web arayüzü ve daha fazlasını tek merkezden yönetir. Hatalardan öğrenir, kendini geliştirir ve tekrarlayan işleri otomatikleştirir.

---

## ✨ Özellikler

### 🤖 Çoklu Bot Yönetimi
- **3 Telegram botu** aynı anda çalıştır
- CLI, web UI ve mesaj platformlarından erişim
- Fan-out: tek mesajı tüm botlara gönder

### 🧠 Akıllı Öğrenme
- **OnceHafiza**: Hatalardan öğrenir, aynı hata tekrarlanmaz
- **Otonom Görev Çözücü**: Karmaşık işlemleri adım adım planlar ve yürütür
- **7+ Yapay Zeka Sağlayıcı**: DeepSeek, OpenAI, Anthropic, Groq, OpenRouter ve daha fazlası

### 🛠️ 100'den Fazla Araç
| Kategori | Araçlar |
|----------|---------|
| 📁 Dosya | Okuma, yazma, düzenleme, arama, bulk replace |
| 🌐 Web | Sayfa çekme, arama, Firecrawl entegrasyonu |
| 🎵 Ses | TTS (sesli okuma), STT (ses tanıma) |
| 🖼️ Görsel | FAL.ai FLUX ile görsel üretme |
| 🎬 Video | yt-dlp ile indirme, ffmpeg ile dönüştürme |
| 💻 Terminal | Shell komutları, Python çalıştırma |
| 🔧 Kod | Syntax kontrol, otomatik düzeltme |

### 📊 Yönetim Araçları
- **Kanban**: Görevleri kartlarla takip et
- **Cost Tracker**: API harcamalarını izle
- **Self-Improvement**: Kalite metriklerini ölç, iyileştir
- **A2A**: Botlar arası mesajlaşma

### 🔌 Gelişmiş
- **MCP İstemci/Sunucu**: Harici MCP araçlarını keşfet ve kullan
- **FTS5 Session Search**: Geçmiş konuşmalarda anında arama
- **Kali/WSL Entegrasyonu**: Linux araçlarını Windows'tan kullan
- **Docker Desteği**: Container ile taşınabilir dağıtım

---

## 📦 Kurulum (Windows)

**Gereksinimler:** Python 3.11+, Git, Windows 10/11

### Otomatik Kurulum (Önerilen)
```powershell
# 1. Repoyu klonla
git clone https://github.com/Watcher-Hermes/ReYMeN-Ajan-v2.git
cd ReYMeN-Ajan-v2

# 2. Kurulum script'ini çalıştır (her şeyi otomatik kurar)
kurulum.bat
```
Script şunları otomatik kurar: Python, Git, VS Code, WSL, ffmpeg, yt-dlp, tüm Python paketleri.

### Manuel Kurulum
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### ⚙️ Yapılandırma
`.env` dosyası oluştur, API anahtarlarını ekle:
```env
DEEPSEEK_API_KEY=sk-...
TELEGRAM_BOT_TOKEN=...
```

---

## 🚀 Kullanım

```bash
# CLI ile başlat
python reymen_launcher.py

# Modül olarak çalıştır
python -m reymen

# MCP sunucu başlat
python -m reymen.core.mcp_server --transport http --port 9000

# Görev çöz
python -c "from reymen.cereyan.motor import Motor; m = Motor(); m.gorev_coz('.ReYMeN/gorev_cozucu_sistemi.md')"
```

---

## 📁 Proje Yapısı

```
reymen/
├── arac/          # 🛠️ Araçlar (web, dosya, ses, görsel, terminal...)
├── cereyan/       # 🧠 Ana işlem döngüsü ve öğrenme
├── core/          # ⚙️ Çekirdek (model adapter, MCP, session search)
├── sistem/        # 🔧 Sistem yönetimi (CLI, gateway, config)
├── guvenlik/      # 🔒 Güvenlik (redact, guardrails, sandbox)
├── hafiza/        # 💾 Hafıza sistemleri
└── scripts/       # 📜 Yardımcı script'ler
```

---

## 🧪 Testler

```bash
python -m pytest tests/ -v
```

Test durumu: **137 passed** ✅

---

## 🤝 Katkıda Bulunma

1. Fork et
2. `feature/xyz` branch'i aç
3. Değişikliklerini yap
4. Testleri çalıştır: `python -m pytest tests/`
5. PR gönder

Detaylı rehber: [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📜 Lisans

**MIT License** — Copyright (c) 2025 Nous Research (Hermes Agent) · 2026 Marko_Pasa_38 (ReYMeN Agent)

Hermes Agent tabanlıdır. Orijinal lisans korunmuştur.

---

<p align="center">
  <b>🇹🇷 Türk geliştiriciler için açık kaynak yapay zeka platformu</b><br>
  <a href="https://github.com/Watcher-Hermes/ReYMeN-Ajan-v2">GitHub</a> •
  <a href="https://github.com/Watcher-Hermes/ReYMeN-Ajan-v2/blob/main/CONTRIBUTING.md">Katkı Rehberi</a> •
  <a href="https://github.com/Watcher-Hermes/ReYMeN-Ajan-v2/blob/main/LICENSE">Lisans</a>
</p>
