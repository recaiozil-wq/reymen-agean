---
skill_id: 3262dd304b9f
usage_count: 1
last_used: 2026-06-16
---
# Frontmatter Standartları

## Zorunlu Alanlar

Her SKILL.md aşağıdaki alanları **kesinlikle** içermelidir:

```yaml
---
name: skill-adi                    # Küçük harf, tire ile ayrılmış, maks 64 karakter
title: "Skill Başlığı"             # Temiz, büyük harfli başlık
tags: [kategori, alt-kategori]     # En az 1 etiket
description: "Use when <trigger>. <one-line behavior>."
version: 1.0.0                     # Semantik versiyonlama
author: ReYMeN User                # Veya gerçek yazar adı
license: MIT                       # Veya uygun lisans
audience: user                     # user | contributor | maintainer
---
```

## Alan Açıklamaları

| Alan | Zorunlu | Açıklama |
|------|---------|----------|
| `name` | EVET | Küçük harf, tire, maks 64 karakter. Dosya adıyla eşleşmeli. |
| `title` | EVET | İnsan tarafından okunabilir başlık. İlk harfler büyük. |
| `tags` | EVET | En az 1 etiket. Kategorileme ve arama için. |
| `description` | EVET | "Use when ..." ile başlamalı, maks 1024 karakter. |
| `version` | ÖNERİLEN | Semantik versiyon: 1.0.0, 1.1.0, 2.0.0 |
| `author` | ÖNERİLEN | Oluşturan kişi. |
| `license` | ÖNERİLEN | MIT, Apache-2.0, vs. |
| `audience` | EVET | user (son kullanıcı), contributor (katkıcı), maintainer (bakımcı) |
| `metadata.hermes.tags` | ÖNERİLEN | skills_list'te görünecek etiketler |
| `related_skills` | ÖNERİLEN | İlişkili skill isimleri dizisi |

## Audience Değerleri

| Değer | Kullanım | Örnek |
|-------|----------|-------|
| `user` | Son kullanıcının doğrudan kullanacağı skill | windows-automation, browser-qa |
| `contributor` | Skill geliştirmeye katkı yapacaklar | skill-creation-standards, skill-shrink |
| `maintainer` | Sadece bakımcıların bilmesi gereken | hermes-kurallar, otomatik-bakim |

## Örnekler

### Basit Skill (user)

```yaml
---
name: ekran-goruntusu-al
title: "Ekran Görüntüsü Alma"
tags: [windows, automation, screenshot]
description: "Use when the user needs to capture the screen on Windows. Supports full screen, active window, and region capture."
version: 1.0.0
author: ReYMeN User
license: MIT
audience: user
---
```

### Karmaşık Skill (contributor)

```yaml
---
name: hibrit-ai-mimarisi
title: "Hibrit AI Mimarisi"
tags: [mlops, architecture, hermes]
description: "Use when designing or troubleshooting ReYMeN' two-layer AI architecture — Ollama (local) + DeepSeek (cloud). Covers routing rules, fallback logic, and model selection."
version: 2.1.0
author: ReYMeN User
license: MIT
audience: contributor
metadata:
  hermes:
    tags: [mlops, architecture, hermes]
    related_skills: [ollama-local-llm, model-benchmark, hibrit-ai-yonlendirme-kurali]
related_skills: [ollama-local-llm, model-benchmark, hibrit-ai-yonlendirme-kurali]
---
```

## Validasyon

```python
# Frontmatter doğrulama için kullanılabilecek kontrol
import yaml, re

with open("SKILL.md") as f:
    content = f.read()

assert content.startswith("---"), "Dosya --- ile başlamalı"
match = re.search(r'\n---\s*\n', content[3:])
assert match, "Frontmatter kapanışı bulunamadı"
fm = yaml.safe_load(content[3:match.start()+3])

# Zorunlu alanlar
required = ["name", "title", "tags", "description", "audience"]
for field in required:
    assert field in fm, f"Eksik zorunlu alan: {field}"

# Karakter limitleri
assert len(fm["name"]) <= 64, f"name çok uzun: {len(fm['name'])}"
assert len(fm["description"]) <= 1024, f"description çok uzun: {len(fm['description'])}"

# audience doğrulama
assert fm["audience"] in ["user", "contributor", "maintainer"], f"Geçersiz audience: {fm['audience']}"
```
