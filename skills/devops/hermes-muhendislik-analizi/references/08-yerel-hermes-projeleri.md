---
skill_id: 1428c19c1018
usage_count: 1
last_used: 2026-06-16
---
# Yerel ReYMeN Projeleri Envanteri

Bu makinede bulunan 4 ReYMeN kod tabanının konumları, durumları ve birbirleriyle ilişkileri.

## 1. ReYMeN Agent (ÇALIŞAN — ŞU ANKİ SİSTEM)

| Özellik | Detay |
|---------|-------|
| Konum | `C:\Users\marko\AppData\Local\hermes\` |
| Durum | ✅ Çalışıyor, aktif kullanımda |
| Model | DeepSeek V4 Flash (custom provider) |
| Konfigürasyon | `.env` dolu, `config.yaml` dolu |
| Skill'ler | 1.045 modüler skill, Router+Reference yapısı |
| Profiller | default (aktif) + diğerleri `~/.hermes/profiles/` |
| CLI | `hermes` komutu kullanılabilir |
| Bağımlılıklar | Python 3.11 venv + npm paketleri |
| Not | Bu sistemle şu an konuşuluyor. Sürekli güncellenir. |

## 2. ReYMeN Agent Ham Repo (KURULU DEĞİL)

| Özellik | Detay |
|---------|-------|
| Konum | `C:\hermes\hermes\` (çift iç içe — `C:\hermes\` içinde `hermes/`) |
| Durum | ❌ Çalışmıyor, kurulum yapılmamış |
| İçerik | Nous Research ReYMeN Agent reposunun tam kopyası |
| Sürüm | v0.15.x (RELEASE_NOTES mevcut) |
| Git | `.git` mevcut (288MB pack), remote origin tanımlı |
| Eksikler | `.env` yok, `cli-config.yaml` yok, venv yok, `pip install` / `uv sync` yapılmamış |
| Büyük dosyalar | `cli.py` (731KB), `run_agent.py` (219KB), `hermes_state.py` (171KB), `conversation_loop.py` (269KB), `agent_init.py` (85KB) |
| Gereksiz | `import yaml.py` (boşluklu isim, 3.6KB) — muhtemelen test amaçlı |
| Not | `C:\Users\marko\AppData\Local\hermes\` ile %99 aynı kod tabanı. Sadece kurulum yapılmamış. |

## 3. ReYMeN Output — Yardımcı Araçlar (KURULU DEĞİL)

| Özellik | Detay |
|---------|-------|
| Konum | `C:\hermes_output\` |
| Durum | ❌ Hiçbir modül çalışmıyor. Kodların tamamı yazılmış, hiçbir fonksiyon boş değil. |
| İçerik | 4 bağımsız modül |

### Modüller

| Modül | Dosya | Satır | Ne Yapar |
|-------|-------|-------|----------|
| Dashboard | `dashboard/app.py` | 338 | FastAPI + HTMX web arayüzü, job CRUD, log viewer, auto-refresh |
| LLM Provider | `llm_provider/provider.py` | 169 | OpenAI/Anthropic/Groq/Ollama, switch_provider, chat |
| LLM Provider | `llm_provider/models.py` | 21 | LLMResponse dataclass |
| Telegram Bot | `telegram_bot/bot.py` | 301 | /run, /status, /logs, /start, /help, background job runner |
| Notion | `notion_integration/notion_writer.py` | 298 | Notion API yazma, verify_connection, CLI desteği |

### Ortak Altyapı
- Tüm modüller aynı `data/jobs.json` dosyasını kullanır
- Dashboard ve Telegram Bot aynı veriyi paylaşır (eşzamanlı yazma koruması yok)
- Her modülün `requirements.txt` ve `.env.example` dosyası mevcut
- API anahtarları eksik (güvenlik gereği boş)

### Çalıştırmak İçin Gerekenler
```bash
# Her modül için ayrı ayrı:
cd C:\hermes_output\<modul>
pip install -r requirements.txt
# .env dosyasını oluştur (ilgili API anahtarlarıyla)
python <modul>.py
```

## 4. ReYMeN — Mini Otonom Ajan (ÇALIŞABİLİR)

| Özellik | Detay |
|---------|-------|
| Konum | `C:\Users\marko\OneDrive\Desktop\ReYMeN Proje\hermes_projesi\` |
| Durum | ✅ Kodlar tamam, derleniyor (0 hata). Ollama kuruluysa çalışır. |
| Sürüm | v1.0 (GUI güvenlik katmanları + görsel onay) |
| Dil | Python 3.10+ |
| LLM | Ollama (varsayılan: llama3.1:8b), DeepSeek fallback |
| Dosya sayısı | 53 Python + dokümanlar |
| Mimari | ReAct döngüsü (main.py → beyin.py → motor.py → araçlar) |
| Araç sayısı | 12 (KOMUT_CALISTIR, PYTHON_CALISTIR, DOSYA_YAZ/OKU, WEB_ARA, TARAYICI_AC, TELEGRAM_GONDER, EKRAN_OKU/TIKLA/NISAN, MAKRO_OYNAT, UYG_ISLEM_CAGIR, HAFIZA_ARA, GOREV_BITTI) |

### Hafıza/Öğrenme (Boş Alanlar)
| Bileşen | Durum |
|---------|-------|
| MEMORY.md | 25 byte (neredeyse boş) |
| USER.md | 10 byte (neredeyse boş) |
| vektor_hafizasi/ | Boş (ChromaDB hiç kullanılmamış) |
| skills/ | 6 beceri kartı (küçük, basit düzeyde) |
| .hermes/makrolar/ | Boş |
| .hermes/nisanlar/ | Boş |
| .hermes/uygulama_hafizasi/ | Boş |

### Çalıştırma
```bash
cd "C:\Users\marko\OneDrive\Desktop\ReYMeN Proje\hermes_projesi"
pip install -r requirements.txt   # chromadb, easyocr, pyautogui vs.
ollama serve                      # ayrı pencerede
python main.py
```

### Paketlenmiş Kopya
`C:\Users\marko\OneDrive\Desktop\ReYMeN Proje\files-2.zip` içinde `hermes_R-eYMeN_v10.zip` — projenin paketlenmiş hali.

---

## İlişki Diyagramı

```
ReYMeN Agent (resmi, Nous Research)     ← KULLANILIYOR
  ├── C:\Users\marko\AppData\Local\hermes\     (kurulu, çalışıyor)
  └── C:\hermes\hermes\                        (ham repo, kurulum yok)

ReYMeN_output (yardımcı araçlar)              ← HİÇ ÇALIŞTIRILMAMIŞ
  └── C:\hermes_output\                        (4 modül, kod tam)

ReYMeN (mini ajan, ReYMeN felsefesi)         ← ÇALIŞABİLİR
  └── Masaüstü/ReYMeN Proje/hermes_projesi/   (53 dosya, Ollama gerek)
```

## Önemli Not
- ReYMeN ve ReYMeN_output, **ReYMeN Agent'ın kendisi değil**, etrafına eklenen yardımcı sistemler
- 4 kod tabanı da birbirinden bağımsız, farklı teknolojiler kullanıyor
- Sadece #1 (ReYMeN Agent, AppData) şu an aktif ve kullanılıyor
