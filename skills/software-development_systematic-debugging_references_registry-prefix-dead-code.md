---
name: software-development_systematic-debugging_references_registry-prefix-dead-code
description: Registry Prefix Mismatch ve Dead Code
title: "Software Development Systematic Debugging References Registry Prefix Dead Code"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Registry Prefix Mismatch ve Dead Code |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Registry Prefix Mismatch ve Dead Code

## 1. Registry Prefix Uyusmazligi

### Belirti

ToolRegistry'den gelen hata motor.py'deki kontrolu geçemez ve hatalı sonuç döner:

```
# Registry döner:
[Hata]: Bilinmeyen arac 'GOREV_BITTI'

# Motor kontrol eder:
if not _registry_sonuc.startswith("[Bilinmeyen arac]"):
    return _registry_sonuc  # ← YANLIŞLIKLA DÖNER!
```

Kontrol `[Hata]:` prefix'ini beklemediği için registry'nin hata mesajını **başarılı sonuç** olarak kabul eder.

### Kok Neden

Registry ve onu çağıran kod farklı prefix formatları kullanır:

| Bileşen | Prefix |
|---------|--------|
| `tool_registry.py` (hata) | `[Hata]: Bilinmeyen arac ...` |
| `motor.py` (kontrol) | `[Bilinmeyen arac]` |

### Cozum

Registry'nin döndüğü prefix'i, çağıranın beklediği formatla uyumlu hale getir:

```python
# tool_registry.py
return f"[Bilinmeyen arac] '{ad}'."      # dogru
# return f"[Hata]: Bilinmeyen arac '{ad}'."  # yanlis (eski)
```

Veya çağırandaki kontrolü genişlet:

```python
if not _registry_sonuc.startswith(("[Bilinmeyen arac]", "[Hata]")):
```

### Tespit

```python
import motor
r = motor._REGISTRY.calistir("OLMAYAN_ARAC", "")
print(f"Prefix: {r[:20]}")
print(f"Starts with [Bilinmeyen arac]: {r.startswith('[Bilinmeyen arac]')}")
```

## 2. Dead Code (Return Sonrasi Kod)

### Belirti

Bir fonksiyonun sonunda tanımlanan araç handler'ları hiçbir zaman çalışmaz:

```python
def calistir(self, arac, params):
    # ... once registry ...
    sonuc = self._fallback_calistir(arac, params)
    return sonuc   # ← BU NOKTADA FONKSIYON BITER
    
    # ASAGIDAKI KOD HIC CALISMAZ (dead code)
    if arac == "GOREV_BITTI":
        return "__GOREV_BITTI__"
    if arac == "PDF_OKU":
        ...
```

### Kok Neden

Kod refactoring sırasında `_fallback_calistir()` metodu ayrıldı ama eski handler'lar `calistir()` içinde kaldı. `_fallback_calistir()` her zaman return ettiği için altındaki kod ölü.

### Cozum

Dead code handler'larını `_fallback_calistir()` metoduna taşı:

```python
def _fallback_calistir(self, arac, params):
    if arac == "GOREV_BITTI":          # ← buraya tasi
        return "__GOREV_BITTI__"
    if arac == "PDF_OKU":
        ...
    return f"[Hata]: Bilinmeyen araç '{arac}'."
```

### Tespit

```bash
# Dead code bul (return'den sonraki satirlar)
grep -n "return\|if arac ==" motor.py | head -30
# veya Python ile:
python -c "
import inspect, ast
src = inspect.getsource(motor.Motor.calistir)
tree = ast.parse(src)
# Return'den sonra if/elif kontrol et
"
```

### Onleme

- Yeni araç eklerken doğrudan `_fallback_calistir()`'e ekle
- `calistir()` ana metodunda sadece: registry → plugin → fallback akışı olsun
- İkinci bir `if arac ==` zinciri varsa, dead code ihtimali yüksektir
