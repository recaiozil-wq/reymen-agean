---
skill_id: d91f4f2a678c
usage_count: 1
last_used: 2026-06-16
---
## 4. Backend'i Başlatma

```bash
cd /c/Users/marko/MoneyPrinterTurbo
.venv/Scripts/python.exe main.py
```

- **Port:** 8080 (varsayılan, `listen_port` ile değiştir)
- **Host:** 0.0.0.0 (varsayılan, `listen_host` ile değiştir)
- **Dokümantasyon:** http://localhost:8080/docs

Doğrulama:
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/docs