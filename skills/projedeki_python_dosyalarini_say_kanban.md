---
name: Projedeki Python dosyalarini say, kanban
description: Tamamlanamadi: tur asimi
created: 2026-06-18
usage_count: 2
last_used: 2026-06-18
---

# Projedeki Python dosyalarini say, kanban

Tamamlanamadi: tur asimi

## Adimlar

ARAC_ADI: "dosya_say_acma")
```python
import os

def dosya_say_acma(path):
    return len([name for name in os.listdir(path) if name.endswith(".py")])

kanban_gorev_ekle(dosya_say_acma(path="/path/to/your/project")
PYTHON_CALISTIR: "import os; print(len([f for f in os.listdir('.') if f.endswith('.py')]))"
KANBAN_EKLE: "Python dosya sayısı", "Dosyaların sayısı: 168")
```python
kanban_gorev_ekle("Python dosya sayısı", "Dosyaların sayısı: 168"

---
## Ek Adimlar / Varyasyon (2026-06-18T20:26:40Z)

ARAC_ADI: "python_calistir"
