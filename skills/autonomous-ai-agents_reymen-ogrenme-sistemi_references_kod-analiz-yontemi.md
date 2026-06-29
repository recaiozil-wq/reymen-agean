---
name: autonomous-ai-agents_reymen-ogrenme-sistemi_references_kod-analiz-yontemi
description: Kod Analiz Yöntemi — 6 Adım
title: "Autonomous Ai Agents Reymen Ogrenme Sistemi References Kod Analiz Yontemi"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Kod Analiz Yöntemi — 6 Adım |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Kod Analiz Yöntemi — 6 Adım

Hermes'in (Reymen'in) sorun bulmak için kullandığı sistematik yöntem. Her kod denetiminde bu adımları sırayla uygula.

## Akış

```
1. DOSYA TARA       → proje yapısını çıkar, hangi dosyalar kime ait
2. DERLEME KONTROL  → ast.parse ile sözdizimi doğrula
3. IMPORT TEST      → her modülü import etmeyi dene
4. BAĞIMLILIK ZİNCİRİ → import zincirini takip et, kırık noktayı bul
5. KARŞILAŞTIR      → beklenen vs gerçek durum farkını çıkar
6. RAPORLA          → bulguları Claude Code'a göndermek için yapılandır
```

## Adım 1: Dosya Tara

Proje kökünde ne var, hangi klasörler Reymen'e ait, hangileri Hermes kopyası.

```python
from pathlib import Path
proje = Path(".")

# Reymen dosyaları (sadece bunlara dokun)
reymen_dosyalari = [
    "motor.py", "yetenek_fabrikasi.py", "closed_learning_loop.py",
    "sistem_talimati.py", "sistem_sinyalleri.py", "insan_arayuzu.py",
    "planlayici.py", "uygulama_hafizasi.py", "vektorel_hafiza.py",
    "izole_laboratuvar.py", "main.py"
]

# Hermes kopyası (dokunma)
hermes_dosyalari = [
    "hermes_state.py", "hermes_cli/", "hermes_logging.py",
    "hermes_time.py", "agent/", "tools/", "gateway/"
]

# Anomali tespit
for f in sorted(proje.glob("*.py")):
    satir = len(f.read_text().splitlines())
    if satir > 2000:
        print(f"[BUYUK] {f.name}: {satir} satir")
    if satir < 10:
        print(f"[KUCUK] {f.name}: {satir} satir")
```

## Adım 2: Derleme Kontrolü

Her .py dosyasını `ast.parse` ile derle, SyntaxError varsa raporla.

```python
import ast
for py in Path(".").rglob("*.py"):
    try:
        ast.parse(py.read_text())
    except SyntaxError as e:
        print(f"[SYNTAX] {py}: {e}")
```

## Adım 3: Import Test

Her modülü tek tek import etmeyi dene. Hata mesajından kırılan yeri bul.

```python
import sys, traceback
moduller = [
    "motor", "yetenek_fabrikasi", "closed_learning_loop",
    "sistem_talimati", "sistem_sinyalleri", "insan_arayuzu",
    "planlayici", "uygulama_hafizasi", "vektorel_hafiza",
    "izole_laboratuvar"
]
for mod in moduller:
    try:
        __import__(mod)
        print(f"[OK] {mod}")
    except Exception as e:
        print(f"[FAIL] {mod}: {e}")
```

## Adım 4: Bağımlılık Zinciri

Import hatası alınca zinciri takip et. Örnek:

```
hermes_state.py
  → from agent.memory_manager import sanitize_context  [BULUNDU]
    → from tools.registry import tool_error              [KIRILDI]
      → tools.registry.py'de tool_error yok
```

Her seviyede hangi dosya/fonksiyon eksik, belirle. Bunu Claude Code'a "şu dosyada şu fonksiyon eksik, ekle" olarak ilet.

## Adım 5: Karşılaştır

Beklenen yapıyla gerçek yapıyı karşılaştır.

| Metrik | Beklenen | Gerçek | Durum |
|--------|----------|--------|-------|
| Reymen dosya sayısı | 11 | 11 | ✅ |
| Hermes test dosyası | referans | 1.578 | ✅ |
| Test_learning_loop.py | 17/17 | 17/17 | ✅ |
| hermes_state import | kırık | kırık | ⚠️ biliniyor |

## Adım 6: Raporla

Bulguları Claude Code'a göndermek için yapılandır:

```python
rapor = f"""GÖREV: {hedef_dosya} düzeltmesi

## Bulgu
{adim_2_3_sonucu}

## Yapılacaklar
1. {adim_4_cozum}
2. {dogrulama_adimi}

## Kısıtlamalar
- Hermes dosyalarına dokunma
- Sadece 11 Reymen dosyasını düzenle
- Test et: python -m pytest test_learning_loop.py -v
"""
```

## Ne Zaman Kullanılır

- Yeni kod denetimi başlatırken
- Hata raporu alındığında
- "Sorun bul" dendiğinde
- Claude Code'a görev devretmeden önce (bulguları hazırla)

## Referans

Bu yöntem `Cod Analiz Döngüsü` becerisinin bir parçasıdır. Detaylı uygulama için `reymen-ogrenme-sistemi` skill'ine bak.
