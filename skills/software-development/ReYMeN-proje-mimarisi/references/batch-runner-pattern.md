---
skill_id: 5ad168b29ad1
usage_count: 1
last_used: 2026-06-16
---
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
