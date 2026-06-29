---
name: software-development_reymen-proje-mimarisi_references_batch-runner-pattern
description: Batch Runner Pattern
title: "Software Development Reymen Proje Mimarisi References Batch Runner Pattern"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Batch Runner Pattern |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Batch Runner Pattern

## Dosya
`batch_runner.py` (215+ satir)

## Bilesenler

### SonucYoneticisi
- Thread-safe (Lock ile)
- Checkpoint destegi (`.checkpoint.json`)
- JSONL cikti (her kayit ayri satir)
- `zaten_tamamlandi_mi()` — tekrari engeller

### gorev_isle()
- AIAgentOrchestrator cagrisi
- Sure olcumu
- Hata yonetimi (try/except)

### hedefleri_yukle()
- .txt: her satir bir hedef
- .jsonl: `{"id": "...", "hedef": "..."}` formatinda

### paralel_calistir()
- threading.Queue ile is dagitimi
- Daemon thread'ler
- Worker fonksiyonu

## Pitfall
`self.learning` `__init__` icinde once tanimlanmali, PromptAssemblyEngine'e gecmeden once:
```python
self.learning = ClosedLearningLoop()  # once
self.prompt_engine = PromptAssemblyEngine(  # sonra
    learning_loop=self.learning,
)
```
