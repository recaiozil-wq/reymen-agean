---
name: autonomous-ai-agents_reymen-ogrenme-sistemi_references_auto-index-performans-pattern
description: auto_index Performans Pattern
title: "Autonomous Ai Agents Reymen Ogrenme Sistemi References Auto Index Performans Pattern"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | auto_index Performans Pattern |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# auto_index Performans Pattern

## Sorun

`ClosedLearningLoop.__init__()` her çağrıldığında `tum_becerileri_indeksle()` çalışır. 5.000+ skill dosyası varken bu FTS5 index taraması ~0.7sn sürer. Testlerde her fixture kurulumunda tekrarlanırsa toplam süre patlar.

Ayrıca test temp dizininde çalışsa bile `SKILLS_DIZINLERI` sabiti = `[ROOT / "skills", ROOT / ".hermes" / "skills"]` ile GERÇEK skills dizinini tarar — temp skills_dir parametresi sadece yeni becerilerin kaydedileceği yeri belirler.

## Çözüm: auto_index Parametresi

```python
class ClosedLearningLoop:
    def __init__(self, db_yolu=None, skills_dir=None, auto_index=True):
        ...
        self._kur()
        if auto_index:
            self.tum_becerileri_indeksle()
```

`auto_index=True` (default) — mevcut davranış, geriye dönük uyumlu.
`auto_index=False` — kurulum yapılır ama index atlanır (testler için).

## Testte Kullanımı

```python
@pytest.fixture
def temp_skills():
    with tempfile.TemporaryDirectory() as tmp:
        skills_dir = os.path.join(tmp, "skills")
        os.makedirs(skills_dir, exist_ok=True)
        loop = ClosedLearningLoop(
            db_yolu=os.path.join(tmp, "test.db"),
            skills_dir=skills_dir,
            auto_index=False  # ← ZORUNLU: yoksa 5.000+ skill taranır
        )
        yield tmp, skills_dir, loop
```

## Performans Karşılaştırması

| Durum | 31 skill | 5.564 skill |
|-------|----------|-------------|
| `auto_index=True` (varsayılan) | 0.7sn | 0.7sn (FTS5 insert) |
| Test: `auto_index=False` | 0.42sn (17 test) | 0.42sn (17 test) |
| Test: `auto_index=True` (5.564 skill) | - | **60sn timeout** ❌ |

## Kural

**Test fixture'larında her zaman `auto_index=False` kullan.** Normal çalışmada (`main.py`) varsayılan `True` kalır.
