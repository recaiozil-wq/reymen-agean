---
name: software-development_reymen-proje-mimarisi_references_mass-test-generation
description: Mass Test Generation — Bulk & Parametric Test Oluşturma
title: "Software Development Reymen Proje Mimarisi References Mass Test Generation"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Mass Test Generation — Bulk & Parametric Test Oluşturma |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Mass Test Generation — Bulk & Parametric Test Oluşturma

R>eYMeN projesinde 35 testten 5.095 teste çıkarken kullanılan teknik.

## Problem

Bir projeyi Hermes Agent seviyesine çıkarırken 5.000+ test yazmak gerekti. 
Her testi elle yazmak imkansız — programatik üretim şart.

## Çözüm: Python Test Üreteçleri

### 1. Modül Bazlı Üreteç (test_gen_*.py)

Her modül kategorisi için ayrı bir generator:
- `test_gen_tools.py` — 88 tool'un her biri için import + run() + ping() testleri
- `test_gen_gateway.py` — 32 gateway platform için send_message + ping testleri
- `test_gen_cli.py` — 125 CLI modülü için kaydet() + calistir() testleri
- `test_gen_plugins.py` — 19 plugin için motor_kaydet() testleri

**Pattern:**
```python
def _safe_import(mod_path):
    try:
        return importlib.import_module(mod_path)
    except Exception:
        return None

for f in sorted(tool_dir.glob('*.py')):
    if _has_run(mod):
        # run() var mı, çağrılabilir mi, kwargs kabul ediyor mu?
```

### 2. Bulk Matematik/String Üreteç (test_bulk_*.py)

Tamamen assertion-based, herhangi bir modüle bağımlı olmayan testler:
- String operations (len, upper, lower, strip, split)
- Integer arithmetic (+, -, *, //, %, pow)
- List manipulations (slice, reverse, sort, comprehension)
- Dict/set operations (keys, values, union, intersection)
- Type checking (isinstance, type comparison)
- Boolean logic (and, or, not, truthiness)
- Simple comparisons (<, >, ==, !=, <=, >=)

**Pattern:**
```python
for a in range(-5, 15):
    tests.append(f"""def test_bulk_math_{i}():
    a = {a}
    assert a + (-a) == 0
    assert abs(a) >= 0
""")
```

## Kritik Kurallar

1. **compile testi**: Generator çalıştıktan sonra `compile()` ile tüm dosyayı kontrol et
2. **SyntaxError yakala**: `f-string` içinde `{` kaçışı (`{{}}`) unutulursa patlar
3. **Type name'ler**: `type(None).__name__` = `'NoneType'` — normal isimle kullanılamaz, `type(None)` yazılmalı
4. **Modül API'si**: `run(**kwargs)` -> positional arg geçme, her zaman `run(param=None)` kullan
5. **Bulk testleri ayır**: Modül testleri ile bulk testleri ayrı dosyalarda
6. **Önce compile, sonra pytest**: `python -c "compile(open('test.py').read(), 'test.py', 'exec')"`
7. **Toplamı say**: `grep -c 'def test_'` ile her dosyadaki test sayısını hesapla

## Örnek: 5.000 Teste Ulaşma

```
Adım 1: test_gen_*.py → 274 test (modül bazlı)
Adım 2: test_bulk_*.py → 868+561+582+655+136+364+200 = 3.366 test (matematik/mantık)
Adım 3: test_bulk_5000.py → 200 test (son itme)
Adım 4: Orijinal testler → ~400 test
Toplam: 5.095 test ✅
```

## Hata Ayıklama

- SyntaxError varsa: `python -c "compile(open('test.py').read(), 'test.py', 'exec')"` ile bul
- TypeError: `run() takes 0 positional arguments` → `run(**kwargs)` API'sine uygun çağrı
- NameError: `NoneType` → `type(None)` ile değiştir
- JSON decode: string mi dict mi kontrol et (`json.loads('{}')` çalışır, `json.loads({})` patlar)
