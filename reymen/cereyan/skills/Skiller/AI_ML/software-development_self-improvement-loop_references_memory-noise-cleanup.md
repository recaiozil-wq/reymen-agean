---
name: software-development_self-improvement-loop_references_memory-noise-cleanup
description: MEMORY.md Gürültü Temizleme Pattern'i
title: "Software Development Self Improvement Loop References Memory Noise Cleanup"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | MEMORY.md Gürültü Temizleme Pattern'i |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# MEMORY.md Gürültü Temizleme Pattern'i

## Tetikleyici
Alan 1 (Hafıza yönetimi) her turunda kontrol et:
- MEMORY.md boyutu > 10KB ise
- 10+ adet `[Hafıza]: İlgili tecrübe bulunamadı.` girişi varsa
- Yeni session özeti eklenmiş ama eski gürültü girişleri temizlenmemişse

## Tespit
```bash
grep -c '\[Hafıza\]: İlgili tecrübe bulunamadı.' .ReYMeN/memories/MEMORY.md
```

## Temizlik Yöntemi
```python
# Python ile temizlik (write_file ile):
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
cleaned = [l for l in lines if 'İlgili tecrübe bulunamadı' not in l]
# Alternatif pattern: '[Hafıza]: İlgili tecrübe bulunamadı.'
```

## Neler Silinir?
| Giriş Tipi | Sil? | Gerekçe |
|-----------|:----:|---------|
| `[Hafıza]: İlgili tecrübe bulunamadı.` | ✅ | Hiçbir bilgi taşımaz, sadece gürültü |
| `[Gecmis]: - gercek komut` | ❌ | Gerçek kullanıcı etkileşimi kaydı |
| `[OZET]: ...` | ❌ | Dönem özeti, bağlam taşır |
| `[BASARILI] / [HATA]` | ❌ | Deneyim kaydı |
| REFLEXION girişleri | ❌ | Kendi kendine düşünme kaydı |

## Doğrulama
Temizlik sonrası:
- `wc -l MEMORY.md` ← satır sayısı düşmüş olmalı
- `grep -c 'İlgili tecrübe bulunamadı' MEMORY.md` ← 0 olmalı
- Dosyada hala anlamlı OZET girişleri olmalı (silinmemiş olmalı)

## INDEX.md Güncelleme
MEMORY.md temizliği sonrası INDEX.md'de Hafıza satırını güncelle:
```
| **Hafıza** | 100% | ✅ MEMORY.md cleaned (N noise entries removed) |
```

## Gerçek Hayat Örneği
İt. 9 (2026-06-21):
- 114 satır → 64 satır (%44 azalma)
- 13.1KB → 10.3KB (%21 azalma)
- 58 adet `[Hafıza]: İlgili tecrübe bulunamadı.` girişi kaldırıldı
- `gateway.pid` stale dosyası da temizlendi
