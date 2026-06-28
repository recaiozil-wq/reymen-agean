---
name: software-development_project-gap-analysis_references_full-verification-scan
description: Full Verification Scan
title: "Software Development Project Gap Analysis References Full Verification Scan"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Full Verification Scan |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Full Verification Scan

Son adim: tum dosyalari, import'lari, syntax'i ve runtime'i dogrula.

## Tek Satirlik Scan

```python
import ast, sys
from pathlib import Path

proje = Path("<proje_yolu>")
py_files = sorted([f for f in proje.rglob("*.py") if "venv" not in str(f) and "__pycache__" not in str(f)])

syntax_ok = sum(1 for f in py_files if ast.parse(f.read_text(encoding="utf-8")))
import_ok = 0
for f in py_files:
    if f.name.startswith("_"): continue
    mod = str(f.relative_to(proje)).replace(".py","").replace("/",".").replace("\\",".")
    try: __import__(mod); import_ok += 1
    except: pass

print(f"Syntax: {syntax_ok}/{len(py_files)}, Import: {import_ok}/{len(py_files)}")
```

## Katmanli Dogrulama

| Katman | Ne Kontrol Edilir | Kriter |
|--------|-------------------|--------|
| **Fiziksel** | Dosya var mi? | `path.exists()` |
| **Syntax** | Derleniyor mu? | `ast.parse()` 0 hata |
| **Import** | Modul yukleniyor mu? | `__import__()` basarili |
| **Entegrasyon** | Ana sisteme bagli mi? | Hedef dosyada `import` satiri var mi? |
| **Runtime** | Calisiyor mu? | `test_suite.py` veya __main__ blogu |

## Entegrasyon Dogrulama (En Kritik)

Dosyalari yazmak isin %50'sidir. Geri kalani entegrasyondur.

```python
# Her yeni dosya icin kontrol et:
# 1. Hedef dosyada import edilmis mi?
for import_edilmesi_gereken in ["iteration_budget", "prompt_builder", "trajectory"]:
    content = open("main.py").read()
    assert import_edilmesi_gereken in content, f"{import_edilmesi_gereken} main.py'de import edilmemis!"
```
