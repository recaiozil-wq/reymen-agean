---
skill_id: 41265fcbe885
usage_count: 1
last_used: 2026-06-16
---
# Batch Runner Pattern

## Ne ise yarar
Birden cok hedefi sirali veya paralel olarak AIAgentOrchestrator ile calistirir.
Checkpoint destegi ile yarida kalan toplu islemlere devam eder.

## Kullanim
```bash
python batch_runner.py --hedefler "rapor hazirla" "veri cek" --paralel 3
python batch_runner.py --dosya hedefler.txt
python batch_runner.py --dosya hedefler.jsonl --paralel 2 --sessiz
```

## Bilesenler
- `SonucYoneticisi`: thread-safe sonuc toplama, checkpoint yukle/kaydet
- `gorev_isle()`: tek hedef -> AIAgentOrchestrator -> sonuc kaydet
- `hedefleri_yukle()`: .txt (her satir bir hedef) veya .jsonl parser
- `paralel_calistir()`: Queue + threading.Thread havuzu

## Bilinen Hatalar
- AIAgentOrchestrator __init__'inde `self.learning` attribute sirasi: 
  `self.learning` ONCE tanimlanmali, kullanim (PromptAssemblyEngine) SONRA gelmeli.
- `__pycache__` guncel degilse AttributeError alinir -> `find . -path "*__pycache__*" -delete`

## Cikti
- JSONL: her satir bir JSON kayit, `logs/batch/batch_YYYYMMDD_HHMMSS.jsonl`
- Checkpoint: `.checkpoint.json` — tamamlanan gorev ID'lerini tutar
