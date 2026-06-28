---
name: software-development_skill-creation-standards_references_router-reference-yapisi
description: Router + Reference Yapısı
title: "Software Development Skill Creation Standards References Router Reference Yapisi"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Router + Reference Yapısı |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Router + Reference Yapısı

## Temel İlke

Bir SKILL.md dosyası **en fazla 3-4 KB** olabilir. Bu limit aşılıyorsa mutlaka Router + Reference modeli kullanılır.

## Router (Ana Dosya) Nedir?

SKILL.md sadece şunları içerir:

- Frontmatter (YAML meta veri)
- Kısa bir genel bakış (1-2 paragraf)
- Ne zaman kullanılacağı
- **references/ altındaki dosyalara linkler**
- Verification checklist

Router dosyası **yürütülecek adımları değil**, hangi referansta hangi bilginin bulunduğunu söyler.

## Reference Dosyaları Nereye Konur?

```
skills/<kategori>/<skill-adi>/
├── SKILL.md              ← Router (≤ 3-4 KB)
├── references/
│   ├── kurulum.md        ← Kurulum adımları
│   ├── api.md            ← API referansı
│   ├── ornekler.md       ← Örnek kullanımlar
│   ├── sorun-giderme.md  ← Hata çözümleri
│   └── ...               ← İhtiyaca göre
├── templates/
│   ├── config.yaml       ← Şablon yapılandırma
│   └── ...
└── scripts/
    └── validate.py       ← Doğrulama scripti
```

## Reference Dosyası İçeriği

Her reference dosyası kendi başına okunabilir olmalıdır:

```markdown
# Dosya Adı - Kısa Açıklama

## Amaç
Bu dosyanın ne için kullanıldığı.

## Adımlar
1. ...
2. ...

## Önemli Uyarılar
- ...
```

## Ne Zaman Bölünmeli?

| Durum | Yapılacak |
|-------|-----------|
| SKILL.md > 4 KB | references/ altına taşı |
| Kod bloğu > 20 satır | references/ altına taşı |
| Tablo > 10 satır | references/ altına taşı |
| Log çıktısı / debug bilgisi | references/ altına taşı |
| 2+ farklı konu anlatılıyor | Her konuya ayrı reference dosyası |

## SKILL.md'den Reference Çağırma

Router dosyasından:
```markdown
Detaylı kurulum → [references/kurulum.md](references/kurulum.md)
API parametreleri → [references/api.md](references/api.md)
```

Ana akış:
```markdown
1. Kurulumu yap (detay: references/kurulum.md)
2. API'yi yapılandır (detay: references/api.md)
3. Doğrula (detay: references/dogrulama.md)
```
