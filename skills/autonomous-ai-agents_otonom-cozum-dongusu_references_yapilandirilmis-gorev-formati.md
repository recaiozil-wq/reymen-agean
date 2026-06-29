---
name: autonomous-ai-agents_otonom-cozum-dongusu_references_yapilandirilmis-gorev-formati
description: Yapilandirilmis Gorev Formati
title: "Autonomous Ai Agents Otonom Cozum Dongusu References Yapilandirilmis Gorev Formati"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Yapilandirilmis Gorev Formati |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Yapilandirilmis Gorev Formati

Kullanici, cozum onerilerini/patch'leri su 4 asamali formatta gormeyi tercih ediyor:

## ASAMA 1: ARASTIRMA
Mevcut durum analizi. Ne var, ne eksik, ne gerekiyor.

## ASAMA 2: SENTEZ
Cozum onerisi. Teknik olarak en verimli yol hangisi? Neden?

## ASAMA 3: UYGULAMA
Somut kod/patch. LLM maliyeti artirmayacak, bagimsiz fonksiyonlar.
- Sonsuz dongu riski engellenmis
- Kontrol insana devredilebilir
- Mevcut mimariyi BOZMAZ (yama olarak eklenir)

## ASAMA 4: DOGRULAMA
Test sonucu. Calisiyor mu? Sonsuz dongu riski var mi?
Insan mudahalesi gerekiyor mu?

### Kullanım
```markdown
## ASAMA 1: ARASTIRMA
...
## ASAMA 2: SENTEZ
...
## ASAMA 3: UYGULAMA
...
## ASAMA 4: DOGRULAMA
...
```
