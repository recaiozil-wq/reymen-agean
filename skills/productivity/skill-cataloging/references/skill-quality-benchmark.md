---
skill_id: b54f9b280b56
usage_count: 1
last_used: 2026-06-16
---
# Skill Quality Benchmark

Tüm ReYMeN skill'lerinin yapısal kalite analizi ve toplu düzeltme prosedürü.

## Ne Zaman Kullanılır

- Skill benchmark puanını sorgularken
- "Skill'lerin kalitesini ölç" dendiğinde
- Toplu frontmatter düzeltmesi gerektiğinde (title, tags, category, parse hataları)
- Yinelenen isimleri temizlerken

## Hızlı Başlangıç (v2 Script)

Python script'i tüm analizi otomatik yapar; `scripts/skill_benchmark.py`:

```bash
python skills/productivity/skill-cataloging/scripts/skill_benchmark.py
```

Çıktı: CSV rapor + özet rapor.
Metrikler: dosya boyutu, satır sayısı, kod bloğu sayısı, referans kullanımı,
frontmatter kalitesi, şişkinlik/teorik etiketi, potansiyel kopya uyarıları.

## Derinlemesine İçerik Benchmark'ı (100 Puan — 4 Kriter)

Her skill'i şu 4 kritere göre değerlendir:

| Kriter | Ağırlık | Açıklama |
|--------|---------|----------|
| **İçerik Kalitesi** | %40 | Amaç net mi? Adım adım talimat, örnekler, edge cases var mı? |
| **Çalışabilirlik ve Mantık** | %25 | Komutlar uygulanabilir mi? Eksik/çelişkili parametre var mı? |
| **Kapsam ve Benzersizlik** | %20 | Odaklı mı? Diğer skill'lerle örtüşüyor mu? |
| **Token Verimliliği** | %15 | Gereksiz tekrar var mı? Kısa ve öz mü? |

**Değerlendirme çıktısı formatı:** Skill Adı, Puan (100), En Güçlü Yön,
En Zayıf Yön, Geliştirme Önerisi (1 cümle).

**Örnek:**
```
self-improvement → 92/100
  Güçlü: Kısa, öz, adım adım, çalıştırılabilir
  Zayıf: İsim çakışması çözümü karmaşık anlatılmış
  Öneri: Referans haritasını reference dosyasında tut
```

## v1 Benchmark Metrikleri (Yapısal)

| Metrik | Açıklama |
|--------|----------|
| title | Frontmatter'da `title` alanı varlığı |
| tags | Frontmatter'da `tags` alanı varlığı |
| category | Frontmatter'da `category` alanı varlığı |
| parse | YAML frontmatter'ın geçerli olma oranı |
| duplicates | Yinelenen name alanı sayısı |
| audience | `audience` alanı varlığı (NemoClaw pattern'i) |

## Adımlar

### 1. Benchmark Çalıştır

```python
from pathlib import Path
import yaml
from collections import Counter

skills_dir = Path("C:/Users/marko/AppData/Local/hermes/skills")

results = {"total": 0, "has_title": 0, "has_tags": 0, "has_category": 0,
           "has_audience": 0, "parse_errors": 0, "duplicates": 0}

for p in skills_dir.rglob("SKILL.md"):
    content = p.read_text(encoding="utf-8", errors="replace")
    if not content.startswith("---"):
        results["parse_errors"] += 1
        continue
    parts = content.split("---", 2)
    if len(parts) < 3:
        results["parse_errors"] += 1
        continue
    try:
        fm = yaml.safe_load(parts[1])
    except:
        results["parse_errors"] += 1
        continue
    results["total"] += 1
    if fm.get("title"): results["has_title"] += 1
    if fm.get("tags"): results["has_tags"] += 1
    if fm.get("category"): results["has_category"] += 1
    if fm.get("audience"): results["has_audience"] += 1

# Puan hesapla (100 üzerinden)
score = (
    results["has_title"]/results["total"]*25 +
    results["has_tags"]/results["total"]*25 +
    results["has_category"]/results["total"]*20 +
    results["has_audience"]/results["total"]*20 +
    (1 - results["parse_errors"]/max(results["total"],1))*10
)
```

### 2. Title Ekle (yoksa)

Name'den otomatik türet:

```python
def generate_title(name):
    title = name.replace("-", " ").replace("_", " ").title()
    abbreviations = {"Ai": "AI", "Api": "API", "Cli": "CLI",
                     "Vscode": "VS Code", "Github": "GitHub",
                     "Ml": "ML", "Llm": "LLM", "Tdd": "TDD"}
    for old, new in abbreviations.items():
        title = title.replace(old, new)
    return title
```

Frontmatter'da `description` varsa ondan sonra, yoksa `name`'den sonra ekle.

### 3. Tag Ekle (yoksa)

Kategori + skill adına göre otomatik tag:

```python
CATEGORY_TAGS = {
    "ecc": ["ai", "automation", "development"],
    "windows-automation": ["windows", "automation"],
    "software-development": ["development", "coding"],
    "devops": ["devops", "system"],
    "creative": ["creative", "design"],
    "mlops": ["mlops", "ai", "machine-learning"],
    "security": ["security", "pentest"],
    # ...
}
```

### 4. Category Ekle (yoksa)

Kök dizin skill'leri için: klasör adını kategori yap.
Kategori klasörleri içindekiler (ecc/, devops/, creative/ vb.): atla (zaten kategorize).

### 5. Parse Hatalarını Düzelt

**Yaygın hatalar:**

| Hata | Sebep | Düzeltme |
|------|-------|----------|
| `mapping values not allowed` | title/description içinde `:` var | Değeri tırnakla sar veya `:` → `—` |
| `while parsing a block mapping` (line 2) | `name:` yanlış yazılmış (`nam:`) | `nam:` → `name:` |
| `while parsing a block mapping` | `related_skills:` fazla girintili | Girintiyi sıfırla (0 indent) |

### 6. Yinelenen İsimleri Düzelt

```python
name_map = {}
for p in skills_dir.rglob("SKILL.md"):
    fm = yaml.safe_load(p.read_text().split("---", 2)[1])
    name = fm.get("name")
    if name:
        name_map.setdefault(name, []).append(p)

for name, paths in name_map.items():
    if len(paths) > 1:
        for p in paths[1:]:
            new_name = f"{name}-{p.parent.name}"
            # name alanını güncelle
```

### 7. Sonuçları Raporla

```
=== SKILL BENCHMARK RAPORU ===
Toplam SKILL.md: 1.185
Title: %99.4
Tags:  %91.8
Category: %99.9
Audience: %100
Parse hatası: ~65 (ECC/baoyu/hersona kaynaklı)
PUAN: ~90/100
```

## Güvenlik

- Frontmatter değişikliği öncesi `.audience-backup/` dizinine TÜM SKILL.md'lerin SHA256 hash'li yedeğini al
- Geri yükleme: `manifest.json` içindeki restore komutunu kullan
- Batch düzeltme sonrası doğrulama yap

## Referans

- NemoClaw pattern'i için: `references/nemoclaw-repo-analysis.md`
- Audience sınıflandırması için: `references/audience-classification.md`
- Örnek benchmark çıktısı: 14 Haziran 2026 — puan 49 → ~90/100
