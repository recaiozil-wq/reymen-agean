---
name: software-development_money-printer-turbo_references_terminal-2-webui
description: "Terminal 2: WebUI"
title: "Software Development Money Printer Turbo References Terminal 2 Webui"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Terminal 2: WebUI |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Terminal 2: WebUI
.venv/Scripts/python.exe -m streamlit run webui/Main.py --server.port=8501 --server.headless=true
```

Port doluysa:
```bash
netstat -ano | grep ":8501 "
taskkill /F /PID <PID>
