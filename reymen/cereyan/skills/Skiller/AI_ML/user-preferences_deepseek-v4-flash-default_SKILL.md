---
name: user-preferences-deepseek-v4-flash-default
description: Bu profil Hermes'in varsayılan modelini tanımlar.
title: User Preferences Deepseek V4 Flash Default
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

bu model aktif olmalıdır.
# DeepSeek V4 Flash — Varsayılan Profil

Bu profil Hermes'in varsayılan modelini tanımlar.

## Yapılandırma

- **Model:** `deepseek-v4-flash`
- **Provider:** `deepseek`
- **Base URL:** `https://api.deepseek.com/v1` (config.yaml'da tanımlı)
- **Context:** 1M token (1048576)

## Kalıcı Varsayılan Yapma

Bu komutlar config.yaml'a yazar, oturumlar arası kalıcıdır:

```bash
hermes config set model deepseek-v4-flash
hermes config set provider deepseek
```

Doğrulama:

```bash
hermes config show | grep -A5 "Model"
# Çıktı: Model: {'default': 'deepseek-v4-flash', 'provider': 'deepseek'}
```

## Hızlı Geçiş (Geçici — Sadece Bu Oturum)

```
/model deepseek
```

Bu komut sadece mevcut oturum için geçerlidir, config.yaml değişmez.

## Notlar

- `hermes config set provider deepseek` doğrudan çalışır — custom provider ayarı gerekmez
- API anahtarı `.env` içinde `DEEPSEEK_API_KEY` olarak tanımlıdır
- 1M context penceresi aktif
- Uzun oturumlarda context dolumunu izle
- Provider adı: `deepseek` (büyük harf, "deep seek" gibi farklı format denemeleri çalışmaz)
