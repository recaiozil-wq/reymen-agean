---
name: software-development_money-printer-turbo_references_5-webui-yi-ba-latma-streamlit
description: 5.
title: "Software Development Money Printer Turbo References 5 Webui Yi Ba Latma Streamlit"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | 5.0 |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## 5. WebUI'yi Başlatma (Streamlit)

```bash
.venv/Scripts/python.exe -m streamlit run webui/Main.py --server.port=8501 --server.headless=true
```

WebUI giriş noktası `webui/Main.py`'dir.

Alternatif: `webui.bat` — port 8501 doluysa 8502-8599 arasında yedek arar.

Doğrulama:
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8501
