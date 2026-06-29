---
name: software-development_self-improvement-loop_references_rotation-cycle-complete
description: Rotation Cycle Completion Pattern
title: "Software Development Self Improvement Loop References Rotation Cycle Complete"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Rotation Cycle Completion Pattern |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Rotation Cycle Completion Pattern

## Ne Zaman Kullanılır
Tüm 5 alan (Hafıza → Planlama → Kod → Hız → Hata) bir kere tamamlandığında.

## Adımlar

### 1. INDEX.md Güncelleme
```
> Son güncelleme: {tarih} {saat}
> Kaynak: Self-Improvement cron — Hata düzeltme (Karar #{N}) — {X}. tur tamam
```
Normal rotasyon satırını güncelle:
```
- Normal rotasyon: {X}. tur tamam ✅ (Hafıza→Planlama→Kod→Hız→Hata)
  ➡️ **{X+1}. tur başlıyor → Hafıza yönetimi** (İt. {N+1})
```

### 2. decisions.md Güncelleme
Karar #N'de (Alan 5 Hata düzeltme) "Sonraki Alan" tablosuna yeni tur satırı ekle:
```
| Sıra | Alan | Durum |
|:----:|------|:-----:|
| 1 | Hafıza yönetimi | ✅ #10 |
| 2 | Planlama | ✅ #11 |
| 3 | Kod kalitesi | ✅ #12 |
| 4 | Hız | ✅ #13 |
| 5 | Hata düzeltme | ✅ **Bu iterasyon** |
| **1** (yeni tur) | **Hafıza yönetimi** | ⏳ Sonraki → **İt. {N+1}** |
```

### 3. Tur Sayacı
- İlk tur: 1. tur (iterations 1-5 veya hangi sırayla gidiyorsa)
- İkinci tur: 2. tur (iterations 6-10)
- INDEX.md son güncelleme satırında tur bilgisi mutlaka olsun

## Örnek
INDEX.md çıktısı:
```
> Son güncelleme: 21 Haziran 2026 17:48
> Kaynak: Self-Improvement cron — Hata düzeltme (Karar #14) — 1. tur tamam

ReYMeN = 99/100 skor. Kalan:
- **Platform** (-2): Discord, Desktop/TUI eklenmeli
- Normal rotasyon: 1. tur tamam ✅ (Hafıza→Planlama→Kod→Hız→Hata)
  ➡️ **2. tur başlıyor → Hafıza yönetimi** (İt. 9)
```
