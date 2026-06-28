---
name: deepseek-v4-flash-default
id: deepseek-v4-flash-default
title: "DeepSeek V4 Flash — Varsayılan Model Profili"
description: "DeepSeek V4 Flash modelini 1M context ile yapılandırır. ReYMeN başlangıcında bu model aktif olmalıdır."
tags: [model, deepseek, config, default, always-active]
category: user-preferences
audience: user
trigger: "session start, /model komutu çalıştırıldığında"
---

# DeepSeek V4 Flash — Varsayılan Profil

Bu profil ReYMeN'in varsayılan modelini tanımlar.

## Yapılandırma

- **Model:** `deepseek-v4-flash`
- **Provider:** custom (DeepSeek doğrudan API)
- **Base URL:** `https://api.deepseek.com/v1`
- **Context:** 1M token (1048576)

## Hızlı Geçiş

```
/model deepseek
```

## Notlar

- API anahtarı config.yaml içinde tanımlıdır
- 1M context penceresi aktif
- Uzun oturumlarda context dolumunu izle
