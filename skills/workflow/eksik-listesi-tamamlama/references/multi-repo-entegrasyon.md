---
skill_id: 10db73817704
usage_count: 1
last_used: 2026-06-16
---
# Multi-Repo Entegrasyon Teknikleri

Bu oturumda öğrenilen teknikler.

## LM Studio Fix (Jinja Hatası)
`llava-v1.6-mistral-7b` "Only user and assistant roles are supported" hatası:
- System mesajını `user` rolüne çevir, başına `[SISTEM]: ` ekle
- `beyin.py` içinde `_cagir_lmstudio()` metodunda uygula

## Çevre Değişkeni Referans Zinciri
ReYMeN Proje `.env` → ReYMeN Agent `.env` çift yönlü senkronizasyon:
1. `main.py`'de `_env_anahtar()` önce kendi .env'ye, bulamazsa `C:\Users\marko\AppData\Local\hermes\.env`'ye bakar
2. `hermes_cli.py`'de `env_aktar()` iki yönlü senkronize eder (biri `***` ise diğerinden doldurur)

## ReAct Loop Koruması
Model aynı eylemi tekrarlıyorsa (`DOSYA_YAZ` → `DOSYA_YAZ`):
- `main.py`'de `onceki_eylem` ve `onceki_param` takibi
- Aynı eylem 2. kez gelince `TEKRAR KORUMASI` devreye girer, görevi bitirir

## Setup Interaktif Kurulum
`reyemen.bat start` → .env'de `***` varsa `setup.py` otomatik çalışır
`setup.py` kullanıcıya sorar: LM Studio/DeepSeek, API anahtarları, Telegram token

## JSON File Lock
Dashboard ve Telegram aynı `data/jobs.json`'a yazıyorsa:
```python
from filelock import FileLock
lock = FileLock(str(LOCK_FILE), timeout=5)
with lock:
    # json oku/yaz
```

## LLM Fallback Zinciri
`provider.py`'de `chat()`: önce mevcut provider'ı dene, başarısız olursa sıradaki provider'a geç. Sıra: mevcut → diğerleri. API key'i olmayan provider'ları atla.
