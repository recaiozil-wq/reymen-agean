# Değişiklik Günlüğü

## [1.0.2] — 2026-07-01

### ✨ Yeni Özellikler
- 📦 **Bağımsız Cron Sistemi** — `reymen/cron/` Hermes'ten bağımsız
  - jobs.py — Cron job depolama ve yönetim
  - scheduler.py — Zamanlanmış görev çalıştırıcı
  - cronjob_tool.py — Agent arayüzü (motor üzerinden cron yönetimi)
- 🌐 **Bağımsız Gateway** — `reymen/gateway/` Telegram platform adaptörü
  - Telegram bot altyapısı Hermes'siz çalışır
  - Python-telegram-bot desteği
  - Session yönetimi, mesaj iletimi
- 🧩 **Hermes Stub'lar** — `hermes_stubs.py` Hermes fonksiyonlarının ReYMeN uyarlaması
  - 40+ Hermes fonksiyonu taklit edildi
  - Gateway + cron + temel sistem için yeterli

### 🔧 İyileştirmeler
- `model_tools.py` + `motor.py` → Hermes import'ları try/except ile korundu
- `pyproject.toml` → cron ve gateway paketleri eklendi
- `.gitignore` → cron_data eklendi
- `README.md` → Kapsamlı kurulum ve kullanım rehberi
- `requirements.txt` → Tüm bağımlılıklar listelendi

### 🐛 Düzeltmeler
- cron `jobs.py` → Veri dizini Python paketi ile çakışmıyor (cron_data)
- cron `cronjob_tool.py` → Hermes import'ları düzgün yönlendirildi

## [1.0.1] — 2026-06-30

### ✨ Yeni Özellikler
- 🔌 **Hermes Bağımsızlığı** — 0 Hermes import bağımlılığı
- 🗄️ **Merkezi Veritabanı** — 21 DB tek merkezde (`reymen/merkez_db/`)
  - Session DB birleştirme (14,146 kayıt)
  - WAL mode + busy_timeout
  - Haftalık WAL checkpoint cron

### 🔧 İyileştirmeler
- `hermes_uyum.py` — Hermes CLI bağımsızlık katmanı
- `.env.example` — Tüm bot token'ları ve API anahtarları
- MIT lisans dosyası
- GitHub Actions CI (Python 3.12)
- Git LFS ile binary dosya yönetimi

## [1.0.0] — 2026-06-20

### ✨ İlk Sürüm
- 🤖 3 Telegram Bot (Pasa_38, Kiral38, ReYMeN_ReYMeNbot)
- 🧠 OnceHafiza + vektör bellek + FTS5 session arama
- 🔧 675+ araç desteği (web, terminal, dosya, browser)
- 📅 Cron job yönetimi
- 🖥️ CLI arayüzü
- 🔒 Güvenlik katmanı
- 📚 Türkçe dokümantasyon
