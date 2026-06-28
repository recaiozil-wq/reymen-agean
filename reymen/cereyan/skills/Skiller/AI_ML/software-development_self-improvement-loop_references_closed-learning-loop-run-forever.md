---
name: software-development_self-improvement-loop_references_closed-learning-loop-run-forever
description: ClosedLearningLoop.run_forever() — Concrete Implementation
title: "Software Development Self Improvement Loop References Closed Learning Loop Run Forever"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | ClosedLearningLoop.run_forever() — Concrete Implementation |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# ClosedLearningLoop.run_forever() — Concrete Implementation

## Konum
`reymen/cereyan/closed_learning_loop.py` — `ClosedLearningLoop` sınıfı içinde.

## Ne Yapar
6 adımlı meta-döngü: **Gözlem → Keşif → Karşılaştır → Dene → Kaydet → Bekle (24h)**

## Metodlar

| Metod | İmza | Açıklama |
|-------|------|----------|
| `observe_self()` | `→ dict` | FTS5'teki tüm becerileri tara, zayıf (kısa açıklamalı) ve strong alanları bul |
| `discover_better_methods(focus)` | `(str) → list[dict]` | DuckDuckGo'da `"best practice {focus} coding"` ara, ilk 5 linki döndür |
| `compare_and_decide(current, new)` | `(dict, list[dict]) → str` | Skor tabanlı: URL varsa +2, ad varsa +1, mevcut farklıysa +1 → UYGULA (≥3) / DAHA_FAZLA_ARAŞTIR (≥1) / REDDET |
| `test_in_sandbox(method)` | `(dict) → (str, float)` | `compile()` ile syntax kontrolü, varsayılan 5.0 + ad 2.0 + kaynak 3.0 = max 10.0 |
| `save_as_skill(method, score)` | `(dict, float) → str` | Mevcut `beceri_kristallestir()` ile skill olarak kaydet |
| `run_forever(cycle_hours=24, test_mode=False, max_test_iter=672)` | `(int, bool, int) → None` | Ana döngü. `test_mode=True` → beklemez, `max_test_iter` kadar iterasyon yapar |

## Test Modu

`run_forever(test_mode=True)` hiç beklemeden sırayla N iterasyonu tamamlar:

```python
# 7 günlük kampanyayı hemen bitir:
loop.run_forever(test_mode=True, max_test_iter=672)

# Hızlı doğrulama (5 iterasyon):
loop.run_forever(test_mode=True, max_test_iter=5)
```

Her iterasyon: observe → discover → compare → decide → (UYGULA ise test + save).  
Test modunda sleep() atlanır, iterasyon sonu `continue` ile bir sonrakine geçer.  
`max_test_iter` iterasyon tamamlanınca döngü kırılır ve `break` ile çıkar.

## Entegrasyon

Self-improvement cron job'ı `run_forever()`'ı background'da başlatır:

```python
from reymen.cereyan.closed_learning_loop import ClosedLearningLoop

loop = ClosedLearningLoop(auto_index=True)
# Tek seferlik elle çalıştırma:
state = loop.observe_self()
discoveries = loop.discover_better_methods(state["weak_areas"][0])
# Background'da sürekli döngü:
import threading
t = threading.Thread(target=loop.run_forever, args=(24,), daemon=True)
t.start()
```

## Sınırlamalar
- **`compare_and_decide()` basit skor kullanıyor** — gerçek Claude/LLM karşılaştırması yok. Geliştirme: API call eklenebilir.
- **`discover_better_methods()` DuckDuckGo HTML scrape** — hızlı, basit ama kırılgan. Geliştirme: `web_search` tool'una geçilebilir.
- **`test_in_sandbox()` compile-only** — gerçek E2B sandbox değil. Geliştirme: E2B API entegrasyonu.
- **run_forever blocking** — thread'de çalıştırılmalı, yoksa main thread'i bloklar.

## Doğrulama

```python
# Smoke test
with tempfile.TemporaryDirectory() as tmpdir:
    loop = ClosedLearningLoop(db_yolu=os.path.join(tmpdir, "test.db"))
    state = loop.observe_self()
    assert "weak_areas" in state
    assert "total_skills" in state
```

Tüm smoke test: `python reymen/cereyan/closed_learning_loop.py`
Tüm pytest: `python -m pytest tests/test_closed_learning_loop.py -v`
