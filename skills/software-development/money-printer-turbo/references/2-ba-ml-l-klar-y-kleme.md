---
skill_id: 662accbdf856
usage_count: 1
last_used: 2026-06-16
---
## 2. Bağımlılıkları Yükleme

**ÖNEMLİ:** `uv.lock` varsa `uv sync` kullan. `pip install -r requirements.txt` ikincildir.

```bash
cd /c/Users/marko/MoneyPrinterTurbo
uv sync
```

`uv sync` şunları yapar:
- `.venv` varsa kontrol eder, eksik paketleri ekler
- `.venv` yoksa oluşturur
- 130+ paketi yükler

### .venv'de pip yoksa sorun değil
MoneyPrinterTurbo `.venv`'i uv ile oluşturulmuş olabilir — pip kurulu olmayabilir.
`uv sync` bunu otomatik çözer.