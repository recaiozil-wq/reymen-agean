---
name: playwright-mcp
title: "Playwright MCP — Tarayıcı Otomasyonu"
tags: [browser, playwright, mcp, web, otomasyon, scraping, test]
description: "Microsoft Playwright MCP ile tarayıcı kontrolü: web gezme, screenshot, form doldurma, JS çalıştırma."
version: 1.0.0
author: ReYMeN Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [Browser, MCP, Web, Otomasyon]
audience: user
related_skills: [native-mcp]
---

# Playwright MCP — Tarayıcı Otomasyonu

Microsoft'un **`@playwright/mcp`** paketi — gerçek tarayıcı oturumu üzerinden web ile etkileşim kurar.

## Hızlı Başlangıç

MCP sunucusu ReYMeN profilinde **otomatik başlatılır** (`config.yaml → mcp_servers.playwright`).

Herhangi bir istek yaz, ReYMeN araçları otomatik kullanır:
- `"github.com aç"` → browser_navigate
- `"sayfayı tara"` → browser_snapshot
- `"ekran görüntüsü al"` → browser_take_screenshot

## Mevcut Araçlar

| Araç | Açıklama |
|------|----------|
| `browser_navigate` | URL'ye git |
| `browser_snapshot` | Sayfa içeriğini metin/accessibility tree olarak al |
| `browser_take_screenshot` | Sayfa ekran görüntüsü |
| `browser_click` | Elemana tıkla |
| `browser_type` | Metin yaz |
| `browser_fill` | Form alanı doldur |
| `browser_select_option` | Dropdown seç |
| `browser_evaluate` | JavaScript çalıştır |
| `browser_wait_for` | Element/durum bekle |
| `browser_go_back` / `browser_go_forward` | Gezinme geçmişi |
| `browser_close` | Tarayıcıyı kapat |
| `browser_network_requests` | Ağ isteklerini listele |
| `browser_console_messages` | Konsol mesajlarını al |

## Kurulum (Manuel)

```powershell
# npx ile doğrudan çalıştır (paket otomatik indirilir)
npx -y @playwright/mcp@latest --headless

# Playwright browserlarını kur (ilk seferinde)
npx playwright install chromium
```

## config.yaml Yapılandırması

```yaml
mcp_servers:
  playwright:
    command: npx
    args:
    - -y
    - "@playwright/mcp@latest"
    - --headless        # görünmez mod — sunucu/otomasyon için
```

Ekstra seçenekler:
```yaml
    args:
    - -y
    - "@playwright/mcp@latest"
    # --headless kaldır → gerçek pencere açar
    - --browser
    - chrome            # chrome / firefox / webkit / msedge
    - --viewport-size
    - "1920x1080"
```

## Kullanım Örnekleri

### Web sayfası okuma
```
"https://example.com adresine git ve sayfa başlığını söyle"
```

### Form doldurma
```
"google.com'a git, arama kutusuna 'playwright mcp' yaz ve ara"
```

### Screenshot
```
"github.com/microsoft/playwright-mcp sayfasının ekran görüntüsünü al"
```

### JavaScript çalıştırma
```
"sayfadaki tüm linkleri JavaScript ile listele"
```

### Detaylı referanslar

| Konu | Dosya |
|------|-------|
| Araç listesi (tam) | `references/tools.md` |
| Yapılandırma seçenekleri | `references/config-options.md` |
| Sorun giderme | `references/troubleshooting.md` |
| Örnekler | `references/examples.md` |
