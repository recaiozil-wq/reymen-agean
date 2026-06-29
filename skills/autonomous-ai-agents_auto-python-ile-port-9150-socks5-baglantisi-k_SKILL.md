---
name: autonomous-ai-agents-auto-python-ile-port-9150-socks5-baglantisi-k
description: '*Olusturuldu: 2026-06-03 06:59 | 1. turde cozuldu*'
title: Autonomous Ai Agents Auto Python Ile Port 9150 Socks5 Baglantisi K
version: 1.0.0
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | AI/ML mühendisi |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | AI/ML görevi gerektiğinde |
| **Neden?** | standardize etmek için |
| **Nasıl?** | Skill adımlarını takip ederek |

et ve sonucu ekrana yaz. Solved in 1 iteration(s) using dolphin-llama3 + VS Code
  loop.'
# Otomatik Cozum: Python ile port 9150 SOCKS5 baglantisi kontrol et ve sonucu ekrana yaz

*Olusturuldu: 2026-06-03 06:59 | 1. turde cozuldu*

## Problem

Python ile port 9150 SOCKS5 baglantisi kontrol et ve sonucu ekrana yaz

## Cozum Kodu

```python
import requests

def kontrol_et():
    url = "http://localhost:9150"

    try:
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            print("Bağlantı başarılı")
        else:
            print(f"Bağlantı başarısız. HTTP kodu: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Bağlantı yapmak için zaman aşımına neden oldu: {e}")

kontrol_et()
```

## Kullanim

```bash
python hermesloop.py "Python ile port 9150 SOCKS5 baglantisi kontrol et ve sonucu ekrana yaz"
```
