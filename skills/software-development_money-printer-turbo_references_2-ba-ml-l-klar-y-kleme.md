---
name: software-development_money-printer-turbo_references_2-ba-ml-l-klar-y-kleme
description: 2.
title: "Software Development Money Printer Turbo References 2 Ba Ml L Klar Y Kleme"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | 2.0 |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

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
