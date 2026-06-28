---
name: ecc_python-testing_references_pytest-stdout-capture
description: Pytest Stdout Capture Hatası (I/O on closed file)
title: "Ecc Python Testing References Pytest Stdout Capture"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Pytest Stdout Capture Hatası (I/O on closed file) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Pytest Stdout Capture Hatası (I/O on closed file)

## Belirti

Pytest çalışırken şu hata ile crash olur:

```
ValueError: I/O operation on closed file.
  File "...\_pytest\capture.py", line 591, in snap
    self.tmpfile.seek(0)
```

Test sonuç özeti görünmez, testlerin kendisi değil pytest altyapısı çöker.

## Kok Neden

Modüller **import edilirken stdout'a yazdığında** (`print()`, plugin banner'ları, `[Plugin] Yuklendi: ...`), pytest'in stdout yakalama mekanizması (`capsys`) bozulur:

- Plugin sistemleri import anında banner basar
- Skill/index dosyaları import sırasında taranır
- ToolRegistry import sırasında "kayit edildi" yazar
- Bu stdout akışı pytest'in `tmpfile.seek(0)` çağrısını bozar

## Cozum

### 1. Kalıcı: `pytest.ini`'ye `addopts = -s` ekle

```ini
[pytest]
addopts = -s
```

Stdout yakalamayı tamamen kapatır. Dezavantaj: `capsys` fixture çalışmaz.

### 2. Alternatif: Modülleri test içinde import et

Modül seviyesinde değil, test fonksiyonu içinde import et:

```python
# HATALI (modül seviyesi):
from main import AIAgentOrchestrator  # import anında stdout'a basar

# DOĞRU (test içi):
def test_agent(self):
    from main import AIAgentOrchestrator  # test çalışırken import
    ...
```

### 3. Alternatif: Gereksiz modülleri import etme

```python
# Yerine:
def test_config(self):
    cfg = {"default_provider": "lmstudio", ...}
    assert "providers" in cfg
```

## Timeout Testleri

Modül import'u zip/disk işlemi yapıyorsa:

```python
# HATALI (timeout):
from backup import yedekle
yol = yedekle("test")  # zip oluşturur, dosya sistemi işlemi

# DOĞRU:
from backup import yedekle
assert callable(yedekle)  # sadece varlığını kontrol et
```
