---
skill_id: 9aaa08abfeb7
usage_count: 1
last_used: 2026-06-16
---
## 1. Clone & Structure Check

```bash
cd /c/Users/marko
git clone https://github.com/harry0703/MoneyPrinterTurbo.git
cd MoneyPrinterTurbo
```

Kök dizin yapısı:
```
MoneyPrinterTurbo/
├── app/                    → FastAPI backend
├── webui/                  → Streamlit WebUI (giriş: webui/Main.py)
├── main.py                 → Backend giriş noktası (uvicorn)
├── webui.bat / webui.sh    → WebUI başlatma
├── cli.py                  → CLI arayüzü
├── config.toml             → Yapılandırma
├── config.example.toml     → Şablon
├── requirements.txt        → pip bağımlılıkları (miras)
├── pyproject.toml          → Proje tanımı
├── uv.lock                 → uv ile kilitlenmiş bağımlılıklar
└── .venv/                  → Sanal ortam
```