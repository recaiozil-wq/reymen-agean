---
name: ortak-bilgi-deposu_references_puanlama-motoru
description: Puanlama Motoru — _puanla.py
title: "Ortak Bilgi Deposu References Puanlama Motoru"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Puanlama Motoru — _puanla.py |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Puanlama Motoru — _puanla.py

Konum: `reymen/sistem/_puanla.py`

Web araması sonucu gelen bilgiyi 4 kriterde puanlar:

| Kriter | Ağırlık | Açıklama |
|:-------|:-------:|:---------|
| Güncellik | 0.3 | 30 gün=1.0, 6 ay=0.8, 1 yıl=0.5, 2 yıl=0.2 |
| Kaynak güven | 0.3 | Resmi doküman=1.0, GitHub=0.9, SO=0.8, Blog=0.6, Forum=0.5 |
| Doğrulama | 0.2 | 3+ kaynak=1.0, 2=0.8, 1=0.5 |
| Çelişki | 0.2 | Uyumlu=1.0, Kısmen=0.6, Çelişki=0.0 |

## Karar
- Puan ≥ 0.7 → KAYDET
- Puan 0.4-0.7 → DANIŞ (kullanıcıya sor)
- Puan < 0.4 → REDDET
