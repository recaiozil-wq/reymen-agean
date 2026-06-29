---
name: autonomous-ai-agents_otonom-cozum-dongusu_references_hermes-modul-entegrasyonu
description: Hermes Modul Entegrasyonu (Reymen Pattern)
title: "Autonomous Ai Agents Otonom Cozum Dongusu References Hermes Modul Entegrasyonu"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Hermes Modul Entegrasyonu (Reymen Pattern) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Hermes Modul Entegrasyonu (Reymen Pattern)

Hermes'ten bir projeye modul kopyalarken:

## Kural

1. Modulu dosya olarak kopyala (tum dosyalariyla)
2. `__init__.py`'si var mi kontrol et
3. Ana projeye (`main.py`) su formatta import et:
   ```python
   try:
       import modul_adi
       _MODUL = modul_adi
   except Exception:
       _MODUL = None
   ```
4. `try/except` kullan — graceful degrade. Modul yoksa None olur, crash olmaz.
5. Bagimli kutuphaneler varsa (`pip install filelock` gibi) kur

## Test

```python
python -c "import sys; sys.path.insert(0, r'proje_yolu'); import main; print(getattr(main, '_MODUL', None))"
```

## Pitfalls

- `sys.path` dogru degilse "No module named" hatasi alirsin — proje dizinini `sys.path.insert(0, ...)` ile ekle
- `__init__.py` yoksa import edemezsin
- Bagimli kutuphaneler eksikse import siradaki try/except'e duser, hata vermez ama modul None olur
