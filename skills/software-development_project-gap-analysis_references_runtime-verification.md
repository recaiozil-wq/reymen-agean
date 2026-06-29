---
name: software-development_project-gap-analysis_references_runtime-verification
description: Runtime Verification — Kod Analizini Doğrulama
title: "Software Development Project Gap Analysis References Runtime Verification"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Runtime Verification — Kod Analizini Doğrulama |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Runtime Verification — Kod Analizini Doğrulama

Yapısal analiz (dosya listesi, import testi) bir projenin **sadece%50'sini** gösterir.
Geri kalan %50: **gerçekten çalışıyor mu?**

## Ne Zaman Kullanılır

- Tüm .py dosyaları import edilebiliyor ama "acaba çalışır mı?" sorusu varsa
- Kullanıcı "çalıştırılamaz durumda mı?" diye sorduğunda
- Eksiklik analizi raporuna **somut kanıt** eklemek istediğinde
- Provider, gateway, web UI gibi ağ/port bağlantılı bileşenler test edilecekse

## Katmanlı Test Sırası

### Katman 1: Import Testi (Tüm Modüller)

```bash
cd "PROJE_YOLU" && python -c "
import sys, os
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

moduller = ['main', 'motor', 'beyin', ...]
basarili = 0; basarisiz = 0
for mod in moduller:
    try:
        __import__(mod)
        basarili += 1
    except Exception as e:
        basarisiz += 1
        print(f'  X {mod}: {str(e)[:80]}')
print(f'OK: {basarili}/{len(moduller)}, HATA: {basarisiz}')
"
```

**Hedef:** Tüm modüllerin import edilebilir olması (0 hata).
**Tuzak:** `.env` eksikse veya API anahtarı yoksa bazı modüller import'ta çökebilir.
  → Fallback kontrolü: `os.environ.get("ANAHTAR", "")` ile güvenli okuma.
  → `.env` yoksa, Hermes Agent `.env`'sinden (`AppData/Local/hermes/.env`) dene.

### Katman 2: Provider Ping Testi

```bash
python -c "
from main import CONFIG
from beyin import Beyin
b = Beyin(CONFIG)
for adim in b._fallback_zinciri:
    print(f'{adim[\"provider\"]}/{adim[\"model\"]}: ping={b.ping(adim[\"provider\"])}')
"
```

**Hedef:** En az 1 provider'ın True dönmesi.
**Tuzaklar:**
- LM Studio yerelse, API çalışıyor olmalı (`http://localhost:1234`)
- DeepSeek/OpenAI/Anthropic API anahtarı gerektirir — fallback zincirinde `***` başlangıçlıysa GEÇERSİZ
- Ping başarısız = provider kapalı veya config yanlış

### Katman 3: Web UI Serve Testi

```bash
timeout 8 python -c "
import sys, threading, time, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
import uvicorn
from web_ui import app

def run():
    uvicorn.run(app, host='127.0.0.1', port=8899, log_level='error')
t = threading.Thread(target=run, daemon=True)
t.start()
time.sleep(2)

try:
    r = urllib.request.urlopen('http://127.0.0.1:8899', timeout=3)
    print(f'HTTP {r.status}: {len(r.read())} bytes')
except Exception as e:
    print(f'HATA: {e}')
"
```

**Hedef:** HTTP 200 dönmesi, en az 1KB içerik.
**Tuzak:** Port çakışması (8899 doluysa 8900 dene).

### Katman 4: MCP Sunucu Testi

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | timeout 3 python -c "
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from mcp_serve import stdio_dongu, TOOLS
print(f'{len(TOOLS)} MCP tool tanimli:')
for t in TOOLS:
    print(f'  - {t[\"name\"]}: {t[\"description\"][:50]}')
"
```

**Hedef:** En az 3-5 tool listelenmesi.
**Tuzak:** stdio_dongu sonsuz döngüdür — output'a yazdırmadan direkt import et.

### Katman 5: Session DB / Veri Kontrolü

```bash
python -c "
import sqlite3
con = sqlite3.connect('PROJE_YOLU/.hermes/session.db')
tables = con.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()
for t in tables:
    count = con.execute(f'SELECT COUNT(*) FROM \"{t[0]}\"').fetchone()[0]
    print(f'  {t[0]}: {count} kayit')
con.close()
"
```

**Hedef:** En az 1 tablo, en az 1 kayıt.
**Anlamı:** session.db doluysa = proje daha önce çalıştırılmış ve veri üretmiş.

### Katman 6: ReAct Döngüsü Son Testi (Canlı)

```bash
timeout 30 python -c "
from main import CONFIG, AIAgentOrchestrator
agent = AIAgentOrchestrator(config=CONFIG, max_tur=2)
sonuc = agent.run_conversation('merhaba de ve bitir')
print(f'SONUC: {sonuc}')
"
```

**Hedef:** Agent'ın bir hedef alıp işlemesi (hatalı da olsa).
**Uyarı:** LLM çağrısı yapar — token tüketir. timeout ile sınırla.

## Raporlama

Test sonuçlarını şu şekilde raporla:

```
RUNTIME TEST SONUCLARI:
  Import testi:    54/54 OK ✅
  Provider ping:   LM Studio=True, DeepSeek=True ✅
  Web UI serve:    HTTP 200 (16KB, 14 endpoint) ✅
  MCP sunucu:      8 tool ✅
  Session DB:      24 kayit ✅
  ReAct dongusu:   Calisti (2 tur) ✅
```

Her ❌ için "kütüphane eksik" mi yoksa "kod hatası" mı olduğunu belirt.
