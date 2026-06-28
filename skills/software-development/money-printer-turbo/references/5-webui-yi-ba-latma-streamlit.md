---
skill_id: ae4198d2e566
usage_count: 1
last_used: 2026-06-16
---
## 5. WebUI'yi Başlatma (Streamlit)

```bash
.venv/Scripts/python.exe -m streamlit run webui/Main.py --server.port=8501 --server.headless=true
```

WebUI giriş noktası `webui/Main.py`'dir.

Alternatif: `webui.bat` — port 8501 doluysa 8502-8599 arasında yedek arar.

Doğrulama:
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8501