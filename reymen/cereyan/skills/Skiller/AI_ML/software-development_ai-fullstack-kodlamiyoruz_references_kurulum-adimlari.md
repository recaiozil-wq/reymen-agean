---
name: software-development_ai-fullstack-kodlamiyoruz_references_kurulum-adimlari
description: KURULUM ADIMLARI
title: "Software Development Ai Fullstack Kodlamiyoruz References Kurulum Adimlari"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | KURULUM ADIMLARI |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## KURULUM ADIMLARI

### ADIM 1 — GitHub Repo Oluştur
```bash
gh repo create prototurk --private --clone
cd prototurk
```

### ADIM 2 — Railway Proje + Servisler
```bash
railway login
railway init
railway add postgresql    # PostgreSQL veritabanı
railway add redis          # Redis cache/queue
```

Railway'de 2 environment oluştur:
- `development` → dev.prototurk.com
- `production` → prototurk.com

### ADIM 3 — Cloudflare R2 Bucket
1. Cloudflare hesabı aç → R2'ye gir
2. Yeni bucket oluştur (ör: `prototurk-cdn`)
3. API token oluştur (public read + private write)
4. CORS ayarlarını yap (frontend domain'ine izin ver)

### ADIM 4 — Resend Hesabı
1. resend.com'a kaydol
2. Domain doğrula (prototurk.com)
3. API key al
4. Email template'lerini hazırla

### ADIM 5 — Railway + GitHub Bağlantısı
```bash
railway link              # Repo'yu Railway'e bağla
railway variables set KEY=VALUE  # environment variable'ları ayarla
```
