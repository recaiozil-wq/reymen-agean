---
name: software-development_money-printer-turbo_references_1-clone-structure-check
description: 1.
title: "Software Development Money Printer Turbo References 1 Clone Structure Check"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | 1.0 |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

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
