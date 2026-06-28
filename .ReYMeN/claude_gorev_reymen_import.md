# ReYMeN Import Hataları Çözüm Görevi (Claude Code)

## Hedef
`reymen/reymen_318_hata_cozum.zip` içindeki 195 Python dosyasındaki tüm **import hatalarını** bul ve çöz.

## Adımlar

### 1. Hazırlık
```bash
cd /path/to/ReYMeN-Ajan
unzip reymen_318_hata_cozum.zip
```

### 2. Tarama
Tüm `.py` dosyalarını tara:
```bash
# Syntax kontrolü
find reymen -name "*.py" ! -path "*/venv/*" ! -path "*/__pycache__/*" -exec python3 -c "
import py_compile, sys
try:
    py_compile.compile('{}', doraise=True)
    print('OK: {}')
except py_compile.PyCompileError as e:
    print('FAIL: {} -> {}')
" \;
```

### 3. Import Test
Her dosyayı tek tek import etmeyi dene (ModuleNotFoundError / ImportError yakala):
```bash
python3 -c "
import os, sys
sys.path.insert(0, 'reymen')
for root, dirs, files in os.walk('reymen'):
    for f in files:
        if f.endswith('.py') and not f.startswith('_'):
            mod = f[:-3]
            try:
                exec(f'from {mod} import *')
                print(f'OK: {mod}')
            except Exception as e:
                print(f'FAIL: {mod} -> {e}')
"
```

### 4. Çözüm Stratejileri (Öncelik Sırasıyla)

| # | Strateji | Ne Zaman |
|---|----------|----------|
| 1 | **pip install** | 3rd-party modül eksikse (`pip install <modul>`), requirements.txt'ye ekle |
| 2 | **try/except ImportError** | Opsiyonel bağımlılıklarda (graceful degrade) |
| 3 | **sys.path ekle** | Proje içi modül bulunamıyorsa |
| 4 | **__init__.py'ye export ekle** | Root shim eksikse |
| 5 | **import yolunu düzelt** | `from beyin` → `from reymen.cereyan.beyin` gibi |

### 5. HATA Kodlarını Güncelle
Çözülen her hata için ilgili `hata_kodlari/HATA-XXXX.md` dosyasında:
```yaml
durum: cozuldu
```
olarak güncelle. Çözüm satırı ekle.

### 6. Doğrulama
```bash
# Tüm dosyalar import edilebiliyor mu?
python3 -c "import reymen.cereyan.motor; print('OK')"

# Testler çalışıyor mu?
cd reymen && python3 -m pytest tests/ -x --tb=short --ignore=tests/test_run.py --ignore=tests/ReYMeN_reference
```

## Kısıtlamalar

- `venv/` ve `__pycache__/` dizinlerine dokunma
- Çalışan kodu bozma (sadece import fix)
- Her değişiklikten sonra syntax kontrolü yap
- Çözülemeyen import'lar için `# TODO: manual fix required` yorumu ekle

## Çıktı Formatı

İşlem sonunda:

```
=== IMPORT HATASI RAPORU ===
Toplam dosya: 195
Hata bulunan: X
Çözülen: Y
Çözülemeyen: Z
Süre: N dk
```
