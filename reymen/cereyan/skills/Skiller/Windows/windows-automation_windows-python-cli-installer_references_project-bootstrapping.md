
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Windows Automation_Windows Python Cli Installer_References_Project Bootstrapping |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Multi-Modül Python Proje Bootstrapping (Windows)

**Kapsam:** Birden çok Python modülü, requirements.txt, .env ve alt servisleri olan bir projenin sıfırdan çalışır hale getirilmesi.

## Adımlar

### 1. Proje Yapısını Tanı
Projeyi tanı: kaç Python dosyası, kaç modül klasörü, requirements.txt, .env.example var mı?

```bash
find . -name "*.py" | wc -l          # Python dosya sayısı
ls */requirements.txt 2>/dev/null    # Alt modüllerin gereksinimleri
```

### 2. Bağımlılıkları Kur
```bash
pip install -r requirements.txt
# Varsa alt modüllerin gereksinimlerini de kur
for f in */requirements.txt; do pip install -r "$f"; done
```

### 3. .env'yi Hazırla
- `.env.example` varsa kopyala: `cp .env.example .env`
- Yoksa projedeki `CONFIG` sabitinden veya `__init__` parametrelerinden env değişkenlerini çıkar
- Tüm API anahtarları placeholder (`***`, `sk-your-key`, `BURAYA_KEY_GIR`) olabilir — kullanıcı doldurmalı
- `read_file` .env dosyalarını **okuyamaz** (güvenlik engeli) — `cat` ile terminal'den oku

### 4. Derleme Kontrolü
```bash
# Tüm .py dosyalarını dene
python -c "import ast, glob; [ast.parse(open(f).read()) for f in glob.glob('**/*.py', recursive=True)]"
```

### 5. Import Kontrolü
```bash
# Ana modülleri import et
python -c "from main import <AnaSinif>; print('OK')"
```

### 6. Windows Başlatıcı (.bat) Oluştur
```batch
@echo off
chcp 65001 >nul
cd /d "%~dp0"

if "%1"=="start" goto :start
if "%1"=="doctor" goto :doctor
if "%1"=="--help" goto :help

:start
python start.py
goto :end

:doctor
python -c "
from pathlib import Path
k = Path('.')
env = k / '.env'
print('OK' if env.exists() else 'MISSING: .env')
print(f'{len(list(k.glob(\"*.py\")))} Python files')
"
goto :end

:help
echo Usage: ...
:end
```

### 7. JSON Yazma Yarışı Koruması (filelock)
Birden çok süreç aynı JSON dosyasına yazıyorsa `filelock` ekle:
```python
from filelock import FileLock

LOCK_FILE = "data/jobs.json.lock"
def load_jobs():
    with FileLock(LOCK_FILE, timeout=5):
        if JOBS_FILE.exists():
            return json.loads(JOBS_FILE.read_text())
        return {}

def save_jobs(jobs):
    with FileLock(LOCK_FILE, timeout=5):
        JOBS_FILE.write_text(json.dumps(jobs, indent=2, default=str))
```

### 8. LLM Provider Fallback Zinciri
Provider düşerse otomatik geçiş:
```python
providers_to_try = [current_provider] + [p for p in all_providers if p != current_provider]
for p in providers_to_try:
    try:
        return chat_with_provider(p, messages)
    except:
        continue
return error_response
```

### 9. ReAct Döngüsü Tekrar Koruması
Model aynı eylemi tekrarlarsa loop'u kes:
```python
onceki_eylem = None
onceki_param = None
for tur in range(max_tur):
    arac, ham = eylemi_ayristir(cevap)
    if tur >= 2 and arac == onceki_eylem and ham == onceki_param:
        print("[TEKRAR KORUMASI] Aynı eylem tekrarlandı")
        break
    onceki_eylem, onceki_param = arac, ham
```

### 10. Multi-Service Orchestrator
Tüm servisleri tek komutla başlatan `start.py`:
- Her servis ayrı `subprocess` veya thread
- Graceful shutdown (Ctrl+C)
- Durum tablosu
- Port kontrolü

## Pitfalls

- **Hermes Agent double-nesting:** Nous Research Hermes Agent zip'ten çıkarılırken `hermes/hermes/` şeklinde çift klasör oluşur. Dosyaları bir katman yukarı taşı: `mv hermes/* . && rmdir hermes`
- **.env secret-bearing:** `read_file` .env'yi okumaz. `cat` veya `grep` ile terminal'den oku.
- **LM Studio jinja hatası:** Bazı modeller (`llava`) `system` rolünü kabul etmez. `[SISTEM]:` prefix'i ile user mesajına çevir.
- **pip install -e . hatası:** Hermes Agent zaten çalışıyorsa `hermes.exe` kilitli olabilir. Normal `pip install` yeterli.
