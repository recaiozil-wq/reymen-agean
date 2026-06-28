---
name: user-preferences_terminal-communication_references_async-task-delivery
description: Async Görev Teslimi (Arkaya Atma Kuralı)
title: "User Preferences Terminal Communication References Async Task Delivery"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Async Görev Teslimi (Arkaya Atma Kuralı) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Async Görev Teslimi (Arkaya Atma Kuralı)

## Kural
Kullanıcı bir görev verdiğinde:
1. Görevi hemen **arka planda** çalıştır (`background=true`, `notify_on_complete=true`)
2. Kullanıcıya hemen **"Tamam, arkada çalışıyor"** cevabını ver
3. Kullanıcı başka soru yazmaya devam edebilir
4. İş bitince **bildirim** gelir

## Kullanılacak Yöntemler

| Görev Türü | Yöntem |
|-----------|--------|
| Script/komut (indir, kopyala, sistem) | `terminal(background=true, notify_on_complete=true)` |
| AI gerektiren (araştır, analiz, kod) | `delegate_task` veya `cronjob(action='run')` |

## Neden?
Kullanıcı beklemez. "Sen işi yaparken ben başka şey yazayım" ister. ASLA kullanıcıyı iş bitene kadar bekletme.

## Cron Temizliği
Kullanıcı minimal cron tercih eder. Çakışan/aynı işi yapan cron'lar birleştirilmeli veya silinmeli.
