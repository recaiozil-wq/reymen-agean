---
name: localhost-servis-yonetimi
title: "Localhost Servis Yonetimi"
tags: [automation, devops, system]
description: >-
  Manage localhost services, ports, health checks, and desktop shortcuts
  for HTTP services (ReYMeN Studio, LM Studio, Streamlit, n8n, etc.)
version: 1.0.0
author: hermes-agent
license: MIT
metadata:
  hermes:
    tags: [localhost, port, servis, dashboard, shortcut, windows]
audience: maintainer
related_skills: []
---

# Localhost Servis Yönetimi

## Overview

ReYMeN'in çalıştırdığı yerel HTTP servislerini yönetmek için:
- Port durumu kontrolü (açık/kapalı)
- Servis başlatma/durdurma
- Masaüstü kısayol oluşturma
- README ile dokümantasyon

## Desktop Shortcut Location

Windows masaüstü kısayolları için DOĞRU YOL:
```
C:\Users\marko\OneDrive\Desktop\ReYMeN-Localhosts\
```

NOT: `C:\Users\marko\Desktop` veya `C:\Users\marko\OneDrive\Masaüstü` DEĞİL.

## Known Services

| Port | Servis | Durum | Başlatma |
|------|--------|-------|----------|
| 9119 | ReYMeN Agent Dashboard | `hermes dashboard --no-open` (background, önce build gerekebilir) |
| 8000 | ReYMeN Output Dashboard | `cd /c/hermes_output/dashboard && python app.py` (background) |
| 1234 | LM Studio API | LM Studio uygulaması → Settings → Local Server |
| 8501 | Streamlit | `streamlit run app.py` (Mevcut bir Streamlit uygulaması varsa) |
| 5678 | n8n | `n8n start --port=5678` (background) |
| 8082 | Web App | Belirlenmedi |
| 7000 | Servis | Belirlenmedi |

NOT: Port 8648'de çalışan ayrı bir "ReYMeN Studio" yoktur. ReYMeN'in web arayüzü `hermes dashboard --port 9119` komutuyla başlatılır.

## Port Health Check

```python
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)
try:
    s.connect(('localhost', PORT))
    print("ACIK")
except:
    print("KAPALI")
finally:
    s.close()
```

## Creating Desktop Shortcuts (.url)

Windows .url dosyası formatı:

```
[InternetShortcut]
URL=http://localhost:PORT
```

Hedef klasöre yaz:

```python
with open(f"{desktop}/ReYMeN-Localhosts/{name}.url", "w") as f:
    f.write(f"[InternetShortcut]\nURL={target}\n")
```

## Pitfalls

1. **YANLIŞ MASAÜSTÜ YOLU** — Asla `C:\\Users\\marko\\Desktop` kullanma. Doğru yol: `C:\\Users\\marko\\OneDrive\\Desktop`
2. **Port değişebilir** — n8n ve ReYMeN Studio alternatif portta başlatılabilir; kontrol et
3. **Servis başlatma onayı** — Yeni servis başlatmadan önce kullanıcıya sor
4. **n8n background** — n8n `&` ile değil, `terminal(background=true)` ile başlat
5. **ReYMeN Dashboard build hatası** — `hermes dashboard` ilk çalıştırmada `Cannot find module 'typescript/bin/tsc'` hatası verirse, şunu çalıştır:
   ```bash
   cd /c/Users/marko/AppData/Local/hermes/hermes-agent
   npm install --workspace web
   ```
   Sonra `hermes dashboard --no-open` tekrar dene. Build ~45 saniye sürer.
6. **`hermes dashboard` arka planda** — `terminal(background=true, notify_on_complete=true)` ile başlat. Build tamamlanınca port 9119 kontrol et.
