# ReYMeN Agent

Bağımsız, çok botlu, yapay zeka ajan platformu.  
Hermes Agent'ten bağımsız — kendi Telegram bot altyapısı ile çalışır.

---

## 📋 Gereksinimler

| Gereksinim | Minimum |
|------------|---------|
| Python | 3.12+ |
| RAM | 4 GB (önerilen: 8 GB) |
| Disk | 500 MB boş alan |
| İşletim Sistemi | Windows 10/11, Linux, macOS |

## 🚀 Hızlı Başlangıç

```bash
# 1. Depoyu klonla
git clone https://github.com/recaiozil-wq/reymen-agean.git
cd reymen-agean

# 2. Bağımlılıkları yükle
pip install -r requirements.txt

# 3. Ortam değişkenlerini ayarla
cp .env.example .env
# .env dosyasını düzenle:
#   - TELEGRAM_BOT_TOKEN_PASA_38=<token>
#   - DEEPSEEK_API_KEY=<key>
#   (diğer botlar ve API'ler opsiyonel)

# 4. Bot'u başlat (Hermes Gateway'siz)
python reymen_bot.py --bot pasa_38
```

## 🤖 Bot Yönetimi

```bash
# Botları listele
python reymen_gateway.py --list

# Tek bot başlat
python reymen_bot.py --bot pasa_38
python reymen_bot.py --bot kiral38
python reymen_bot.py --bot reymen

# Gateway ile tüm botları yönet
python reymen_gateway.py --all
```

## ⏰ Cron Job Yönetimi

Cron job'ları ReYMeN motoru üzerinden oluşturup yönetebilirsiniz:

```python
from reymen.cron.cronjob_tool import cronjob

# Job oluştur
cronjob(action='create', name='gunluk_ozet', schedule='0 9 * * *',
        prompt='Günlük özet hazırla')

# Job listele
cronjob(action='list')

# Job durdur
cronjob(action='pause', job_id='abc123')
```

## 🧩 Özellikler

| Özellik | Açıklama | Durum |
|---------|----------|:-----:|
| 🤖 **3 Telegram Bot** | Pasa_38, Kiral38, ReYMeN_ReYMeNbot | ✅ |
| 🧠 **Gelişmiş Hafıza** | OnceHafiza, vektör bellek, FTS5 session arama | ✅ |
| 🔧 **Tool Desteği** | Web arama, terminal, dosya, browser | ✅ |
| 🗄️ **Merkezi Veritabanı** | Tüm DB'ler `reymen/merkez_db/` altında | ✅ |
| ⏰ **Cron Job'lar** | Zamanlanmış görev yönetimi | ✅ |
| 🌐 **Bağımsız Gateway** | Hermes'siz Telegram bot altyapısı | ✅ |
| 🪄 **Hermes Stub'lar** | Hermes fonksiyonlarının ReYMeN uyarlaması | ✅ |
| 🖥️ **Web UI** | Tarayıcıdan yönetim arayüzü | ❌ (planlandı) |
| 🧩 **Plugin Sistemi** | Harici eklenti desteği | ❌ (planlandı) |
| 🖼️ **Görsel Üretim** | FAL.ai ile görsel oluşturma | ❌ (planlandı) |
| 🎤 **Ses İşleme** | TTS/STT sesli konuşma | ❌ (planlandı) |

## 📁 Dizin Yapısı

```
ReYMeN-Ajan/
├── reymen/
│   ├── ag/            → Telegram bot, bot süpervizörü
│   ├── arac/          → Araç motoru ve tool'lar
│   ├── cereyan/       → Beyin, motor, konuşma döngüsü
│   ├── cron/          → ⏰ Bağımsız cron sistemi
│   ├── gateway/       → 🌐 Telegram platform adaptörü
│   ├── hafiza/        → Hafıza sistemleri
│   ├── sistem/        → CLI, tool registry, config
│   ├── core/          → Session search, vektör bellek
│   ├── guvenlik/      → Güvenlik kontrolleri
│   └── merkez_db/     → Tüm veritabanları (21 DB)
├── durum.json         → Bot durumu ve yapılandırma
├── reymen_bot.py      → Bağımsız bot başlatıcı
├── reymen_gateway.py  → 🌐 Gateway başlatıcı
├── requirements.txt   → Python bağımlılıkları
├── .env.example       → Örnek ortam değişkenleri
├── pyproject.toml     → Proje yapılandırması
└── LICENSE            → MIT Lisansı
```

## 🔗 Bağlantılar

- [GitHub](https://github.com/recaiozil-wq/reymen-agean)
- [Hata Bildir](https://github.com/recaiozil-wq/reymen-agean/issues/new/choose)

## 📜 Lisans

MIT License.  
Hermes Agent (Nous Research) kaynak kodundan uyarlanan dosyalar (`model_tools.py`, `motor.py`, `cron/`, `gateway/`) Apache 2.0 lisansıyla uyumludur.
