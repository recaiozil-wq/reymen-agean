---
name: autonomous-ai-agents_reymen-ogrenme-sistemi_references_read-only-teardown-pattern
description: Read-Only Teardown Pattern (Windows)
title: "Autonomous Ai Agents Reymen Ogrenme Sistemi References Read Only Teardown Pattern"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Read-Only Teardown Pattern (Windows) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Read-Only Teardown Pattern (Windows)

## Problem

Bir test read-only dosya oluşturur, test biter. `finally` bloğunda `os.chmod` ile izinleri geri vermek gerekir. Ama Windows'ta:

1. `os.chmod` OneDrive kilitli dosyalarda `PermissionError` fırlatır
2. Read-only dosya `TemporaryDirectory` tarafından silinemez → context manager patlar
3. `shutil.rmtree` da aynı hatayı alır

## Çözüm: 3 Kademeli Teardown

```python
import os
import stat
import subprocess
import shutil
import tempfile

def zorunlu_yazilabilir_yap(dosya_yolu):
    """Dosyayi zorunlu olarak yazilabilir yap."""
    # Kademe 1: os.chmod
    try:
        os.chmod(dosya_yolu, stat.S_IRUSR | stat.S_IWUSR)
        return
    except PermissionError:
        pass

    # Kademe 2: Windows attrib -R
    try:
        subprocess.run(["attrib", "-R", str(dosya_yolu)],
                       capture_output=True, timeout=5)
        return
    except Exception:
        pass

    # Kademe 3: Dosyayi silip yeniden olustur
    try:
        icerik = dosya_yolu.read_text(encoding="utf-8", errors="replace")
        dosya_yolu.unlink()
        dosya_yolu.write_text(icerik, encoding="utf-8")
    except Exception:
        pass  # Bu da olmazsa rmtree(ignore_errors) temizler
```

## Temp Dizin Fixture (pytest)

```python
@pytest.fixture
def temp_skills():
    """TemporaryDirectory YERINE mkdtemp + manuel cleanup."""
    import shutil
    tmp = tempfile.mkdtemp()
    try:
        # test kodu
        yield tmp, skills_dir, loop
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
```

## Neden Çalışır

| Kademe | Ne zaman çalışır | Başarısız olursa |
|--------|-----------------|------------------|
| `os.chmod(S_IWUSR)` | Çoğu Windows dosyası | OneDrive/antivirus kilidi |
| `attrib -R` | Her zaman (kernel seviyesi) | Dosya başka process'te açık |
| Sil+yeniden oluştur | Her zaman (yeni dosya = yeni izin) | Çok nadir |
| `rmtree(ignore_errors)` | Son çare | Yok |
