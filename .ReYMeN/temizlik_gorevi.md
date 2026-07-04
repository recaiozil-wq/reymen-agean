# ReYMeN-Ajan Temizlik Görevi

## NE
ReYMeN-Ajan projesindeki yapısal dağınıklığı temizle. Çekirdek sağlam ama etrafta ölü dosyalar ve ReYMeN mirası var.

## NIYE
Tek CLI, tek entry point, temiz dosya yapısı. Sorunsuz çalışmaya devam etmeli.

## ÖN KONTROL — Tüm stub'lar %100 ölü (0 import, 0 referans)

| Dosya | Durum | İşlem |
|-------|-------|-------|
| `beyin.py` (11 s) | Sadece `from reymen.cereyan.beyin import *` | **SİL** ✅ |
| `motor.py` (10 s) | Sadece `from reymen.cereyan.motor import *` | **SİL** ✅ |
| `once_hafiza.py` (4 s) | Sadece `from reymen.cereyan.once_hafiza import *` | **SİL** ✅ |
| `conversation_loop.py` (38 s) | Shim + _Budget sınıfı (kullanılmıyor) | **SİL** ✅ |
| `cli.py` (3 s) | Sadece `from reymen.sistem.cli import *` | **SİL** ✅ |
| `cron_scheduler.py` (3 s) | Sadece `from reymen.sistem.cron_scheduler import *` | **SİL** ✅ |
| `main.py` (18 s) | runpy.run_path ile gerçek main'i başlatır | **KAL** — entry point |

## NASIL

### ADIM 1: 6 Stub Dosyayı Sil
```python
import os
root = r"C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan"
stubs = ["beyin.py", "motor.py", "once_hafiza.py", "conversation_loop.py", "cli.py", "cron_scheduler.py"]
for s in stubs:
    p = os.path.join(root, s)
    if os.path.exists(p):
        os.remove(p)
        print(f"Silindi: {s}")
```

### ADIM 2: Backup Klasörlerini .gitignore'a Ekle
Şu yolları `.gitignore`'a ekle (SİLME, sadece ignore):
```
# Backup / Mirrors
hermes-memory-backup/
hermes_full_backup/
ReYMeN_mirror/
skills_backup/

# Build artifacts
desktop/node_modules/
desktop/dist/
desktop/out/
```

### ADIM 3: Çift Modül Drift Tespiti
Aşağıdaki çiftleri bul ve RAPORLA (birleştirme yapma):
- `reymen/cereyan/once_hafiza.py` vs `reymen/sistem/once_hafiza.py`
- `reymen/cereyan/conversation_loop.py` vs `reymen/cereyan/agent/conversation_loop.py` (varsa)
- `reymen/cereyan/beyin.py` vs `reymen/agent/beyin.py` (varsa)

### ADIM 4: Son Kontrol
```bash
# Tüm import'lar çalışıyor mu kontrol
python -c "from reymen.cereyan.beyin import Beyin; print('beyin OK')"
python -c "from reymen.cereyan.motor import Motor; print('motor OK')"
python -c "from reymen.cereyan.once_hafiza import *; print('once_hafiza OK')"
python -c "from reymen.sistem.cli import *; print('cli OK')"
python -c "from reymen.sistem.cron_scheduler import *; print('cron_scheduler OK')"
```

### ADIM 5: Rapor
```
╔══════════════════╦══════════╗
║ İşlem            ║ Değer    ║
╠══════════════════╬══════════╣
║ Stub silinen     ║ 6        ║
║ Ignore eklenen   ║ N klasör ║
║ Çift modül       ║ N adet   ║
║ Import test      ║ OK/FAIL  ║
╚══════════════════╩══════════╝
```

## YASAKLAR
- ASLA `pip install` yapma
- ASLA kod taşıma/birleştirme yapma (sadece raporla)
- ASLA `rm -rf` ile silme (ignore et)
- ASLA mevcut çalışan kodu değiştirme
- ASLA test çalıştırma (sadece import kontrol)
- main.py'yı SİLME (entry point)
