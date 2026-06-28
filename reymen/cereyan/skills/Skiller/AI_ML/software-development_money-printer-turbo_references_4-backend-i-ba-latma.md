---
name: software-development_money-printer-turbo_references_4-backend-i-ba-latma
description: 4.
title: "Software Development Money Printer Turbo References 4 Backend I Ba Latma"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | 4.0 |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

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
