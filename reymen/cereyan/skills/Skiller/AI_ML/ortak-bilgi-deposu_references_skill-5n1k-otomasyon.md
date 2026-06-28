---
name: ortak-bilgi-deposu_references_skill-5n1k-otomasyon
description: Skill 5N1K Otomasyonu
title: "Ortak Bilgi Deposu References Skill 5N1K Otomasyon"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Skill 5N1K Otomasyonu |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Skill 5N1K Otomasyonu

Konum: `reymen/sistem/skill_5n1k_otomasyon.py`
Cron: Her gün 05:00'te çalışır.

## Ne yapar?
1. `reymen/cereyan/skills/` altındaki tüm .md dosyalarını tara
2. 5N1K tablosu (`| **Kim?** |`) olmayanlara otomatik ekle
3. Dosya adı ve kategoriden Kim/Ne çıkar
4. Kategori emojisi ata (kali→🐉, windows→🪟, reymen→⚙️)
5. Rapor gönder

## 5N1K Formatı (ZORUNLU)
```markdown
```
