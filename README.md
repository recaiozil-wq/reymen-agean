# ReYMeN Agent

Bağımsız, çok botlu, yapay zeka ajan platformu.

## Özellikler

- 🤖 **3 Telegram Bot** — Pasa_38, Kiral38, ReYMeN_ReYMeNbot
- 🧠 **Gelişmiş Hafıza** — OnceHafiza, vektör bellek, FTS5 session arama
- 🔧 **Tool Desteği** — Web arama, terminal, dosya işlemleri, browser
- 🗄️ **Merkezi Veritabanı** — Tüm DB'ler `reymen/merkez_db/` altında
- ⚡ **WAL Mode** — Concurrent okuma/yazma desteği
- 📅 **Cron Job'lar** — Otomatik bakım, WAL checkpoint, disk izleme
- 🔌 **Hermes Bağımsız** — Kendi Telegram bot altyapısı ile çalışır

## Hızlı Başlangıç

```bash
# 1. Ortam değişkenlerini ayarla
cp .env.example .env
# .env dosyasını düzenle: TELEGRAM_BOT_TOKEN_PASA_38, TELEGRAM_BOT_TOKEN_KIRAL38, vb.

# 2. Bot'u başlat (Hermes Gateway'siz)
python reymen_bot.py --bot pasa_38

# 3. Bot'u listele
python reymen_bot.py --list
```

## Dizin Yapısı

```
ReYMeN-Ajan/
├── reymen/
│   ├── ag/            → Telegram bot, bot süpervizörü
│   ├── cereyan/       → Beyin, motor, konuşma döngüsü
│   ├── hafiza/        → Hafıza sistemleri
│   ├── sistem/        → CLI, tool registry, config
│   ├── core/          → Session search, vektör bellek
│   └── merkez_db/     → Tüm veritabanları (21 DB, 158MB)
├── durum.json         → Bot durumu ve yapılandırma
├── reymen_bot.py      → Bağımsız bot başlatıcı
└── LICENSE            → MIT Lisansı
```

## Lisans

MIT License. Hermes Agent'ten esinlenilen kodlar (model_tools.py, motor.py)
Apache 2.0 lisansıyla uyumludur.
