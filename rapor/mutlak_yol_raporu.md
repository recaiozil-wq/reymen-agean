# ReYMeN-Ajan — Mutlak Yol Taraması, .gitignore & Bağımlılık Raporu

**Tarih:** 2026-07-02
**Proje:** `C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan`

---

## 1. .gitignore Analizi

Dosya: `.gitignore` (126 satır, kapsamlı)

### Kontrol Listesi

| Öğe | Durum | Açıklama |
|-----|-------|----------|
| `.env` gizleniyor mu? | ✅ | Satır 10: `.env` |
| `.env.example` var mı? | ❌ | `.env.example` dosyası projede **yok** (öneri: oluşturulmalı) |
| SQLite/chromaDB ignore? | ✅ | `*.db` (34), `chroma_db/` (126), `analitik.db` (37) |
| `__pycache__` / `*.pyc` | ✅ | Satır 25-26: `*.pyc`, `__pycache__/` |
| `venv/.venv` | ✅ | Satır 4-5: `.venv/`, `venv/`, `env/` |
| `logs/` | ✅ | Satır 29-30: `*.log`, `logs/` |
| IDE (.vscode/.idea) | ✅ | Satır 16-17: `.vscode/`, `.idea/` |
| OS (.DS_Store/Thumbs.db) | ✅ | Satır 23-24: `.DS_Store`, `Thumbs.db` |
| `*.egg-info/` | ✅ | Satır 7 |
| `dist/` / `build/` | ✅ | Satır 52-53 |

### Eksik / Öneriler

1. **`.env.example` eksik:** `.env` git'ten gizleniyor ama örnek bir `.env.example` dosyası yok. Yeni geliştiricilerin hangi env değişkenlerinin beklendiğini anlaması için `.env.example` oluşturulması önerilir.
2. **`.python-version` eklenebilir:** pyproject.toml Python >=3.11 gerektiriyor, `.python-version` dosyası varsa ignore edilebilir.

---

## 2. Mutlak Yol Taraması

### 2.1 src/reymen/ — Canlı Kod Dosyaları

#### A. container_sandbox.py — Dokümantasyon/String Örnekleri (Düşük Risk)

| Satır | Bulunan Yol | Tür |
|-------|------------|-----|
| 184 | `"/c/Users/marko/proje"` | Docstring örnek (showcase) |
| 404 | `C:\\Users\\marko\\proje` | Docstring örnek |
| 405 | `C:/Users/marko/proje` | Docstring örnek |
| 412 | `C:\\Users\\marko` | Docstring örnek |

**Değerlendirme:** Bunlar `_windows_yol_duzelt()` metodunun nasıl çalıştığını gösteren dokümantasyon örnekleridir. Çalışma zamanında bu yollar kullanılmaz. `_windows_yol_duzelt()` fonksiyonu herhangi bir Windows yolunu dinamik olarak Docker mount yoluna çevirir — doğru implementasyon.

#### B. platform_adapter.py — Dokümantasyon/String Örneği (Düşük Risk)

| Satır | Bulunan Yol | Tür |
|-------|------------|-----|
| 12 | `r"C:\\Users\\marko\\proj"` | Docstring örnek |
| 199-200 | `C:\\Users\\foo` | Genel açıklama |
| 217-218 | `C:\\Users\\foo` | Yol dönüşüm açıklaması |

**Değerlendirme:** `translate_path()` ve `to_windows_path()` fonksiyonlarının nasıl çalıştığını açıklayan dokümantasyon. `C:\\Users\\marko\\proj` satır 12'de bir docstring'de geçiyor. Düzeltme: `C:\\Users\\kullanici\\proj` gibi genel bir örnek kullanılabilir.

#### C. tools/obsidian_tool.py — Dokümantasyon Örnekleri (Düşük Risk)

| Satırlar | Bulunan Yol | Tür |
|----------|------------|-----|
| 351 | `C:/Users/marko/Obsidian Main` | Docstring örnek |
| 388 | `C:/Users/marko/Obsidian Main` | Docstring örnek |
| 424 | `C:/Users/marko/Obsidian` | Docstring örnek |
| 511, 545 | `C:/Users/marko/Obsidian` | Docstring örnek |
| 579, 604 | `C:/Users/marko/Vault` | Kullanıcı mesajı örneği |

**Değerlendirme:** Bunlar kullanıcıya örnek vermek için kullanılan string'lerdir. Kullanıcı kendi vault yolunu belirteceği için fonksiyonel bir sorun yok. Ancak `marko` kullanıcı adı yerine `kullanici` gibi genel bir örnek kullanılması daha iyi olur.

#### D. tor_otomasyonu.py — **KRİTİK: Çalışma Zamanı Absolute Path**

| Satır | Bulunan Yol | Tür |
|-------|------------|-----|
| 82 | `Path(f"C:\\Users\\{kullanici}\\Desktop\\Tor Browser\\Browser\\firefox.exe")` | **Çalışma zamanı kodu** |
| 83 | `Path(f"C:\\Users\\{kullanici}\\Masaüstü\\Tor Browser\\Browser\\firefox.exe")` | **Çalışma zamanı kodu** |
| 84 | `Path("C:\\Tor Browser\\Browser\\firefox.exe")` | **Çalışma zamanı kodu** |
| 85 | `Path("C:\\Program Files\\Tor Browser\\Browser\\firefox.exe")` | **Çalışma zamanı kodu** |

**Risk:** YÜKSEK — Bu yollar sadece varsayılan Tor Browser kurulum yollarını arar. Kullanıcı Tor'u farklı bir dizine kurmuşsa veya farklı bir Windows kullanıcısı kullanıyorsa (`kullanici` değişkeni her zaman doğru olmayabilir) çalışmaz.

**Önerilen Düzeltme:**
```python
# Dinamik yol çözümü
from pathlib import Path
import winreg

def _tor_bul():
    # 1. Kayıt defterinden dene
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe") as key:
            return Path(winreg.QueryValue(key, None)).parent
    except:
        pass

    # 2. Varsayılan konumlar (dinamik home ile)
    home = Path.home()
    local = Path(os.environ.get('LOCALAPPDATA', home / 'AppData' / 'Local'))
    prog_files = Path(os.environ.get('ProgramFiles', 'C:\\Program Files'))

    adaylar = [
        home / 'Desktop' / 'Tor Browser' / 'Browser' / 'firefox.exe',
        home / 'Masaüstü' / 'Tor Browser' / 'Browser' / 'firefox.exe',
        local / 'Tor Browser' / 'Browser' / 'firefox.exe',
        prog_files / 'Tor Browser' / 'Browser' / 'firefox.exe',
    ]
    return next((p for p in adaylar if p.exists()), None)
```

#### E. file_safety.py — Sistem Koruması (Orta Risk)

| Satır | Bulunan Yol | Tür |
|-------|------------|-----|
| 18-26 | `C:\\Windows`, `C:\\Program Files`, `/etc`, `/boot`, vs. | **Çalışma zamanı kodu** |

**Değerlendirme:** Bu dizinler sistem güvenliği için yasaklanmış dizinler listesidir. Windows'a özgü olmaları normaldir. Ancak `os.environ.get('SystemRoot', 'C:\\Windows')` kullanılarak dinamik hale getirilebilir.

**Önerilen Düzeltme:**
```python
import os
system_root = os.environ.get('SystemRoot', 'C:\\Windows')
program_files = os.environ.get('ProgramFiles', 'C:\\Program Files')
program_files_x86 = os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')

YASAK_DIZINLER = [
    system_root,
    os.path.join(system_root, 'System32'),
    os.path.join(system_root, 'System'),
    program_files,
    program_files_x86,
    '/etc', '/boot', '/dev',
]
```

#### F. network_restriction.py — Sistem Dosya Yolu (Orta Risk)

| Satır | Bulunan Yol | Tür |
|-------|------------|-----|
| 51 | `r"C:\\Windows\\System32\\drivers\\etc\\hosts"` | **Çalışma zamanı kodu** |
| 52 | `r"C:\\Windows\\SysWOW64\\drivers\\etc\\hosts"` | **Çalışma zamanı kodu** |

**Önerilen Düzeltme:**
```python
system_root = os.environ.get('SystemRoot', 'C:\\Windows')
HOSTS_DOSYASI = os.path.join(system_root, 'System32', 'drivers', 'etc', 'hosts')
HOSTS_DOSYASI_ALT = os.path.join(system_root, 'SysWOW64', 'drivers', 'etc', 'hosts')
```

#### G. conversation_loop.py & vision_tools.py — Dokümantasyon (Düşük Risk)

| Dosya | Satır | Bulunan |
|-------|-------|---------|
| conversation_loop.py | 1365 | `C:\\...` — docstring'de path pattern örneği |
| conversation_loop_run_conversation_yedek.py | 1265 | `C:\\...` — docstring'de path pattern örneği |
| vision_tools.py | 8 | `C:\\Users\\...\\foto.png` — docstring örneği |

**Değerlendirme:** Sadece dokümantasyon, kod çalışma mantığını etkilemez.

### 2.2 reymen/ (Kök Seviye Scriptler) — **KRİTİK**

#### H. tbench_plan_recovery.py — **KRİTİK**

| Satır | Bulunan Yol |
|-------|------------|
| 10 | `BASE = r"C:\\Users\\marko\\Desktop\\Reymen Proje\\ReYMeN-Ajan\\terminal-bench-benchmark\\original-tasks"` |
| 12 | `RESULTS_FILE = r"C:\\Users\\marko\\Desktop\\Reymen Proje\\.ReYMeN\\reports\\tbench-plan-recovery.json"` |

**Önerilen Düzeltme:**
```python
from pathlib import Path
KOK = Path(__file__).parent.parent.resolve()  # ReYMeN-Ajan dizini
BASE = str(KOK / "terminal-bench-benchmark" / "original-tasks")
RESULTS_FILE = str(KOK / ".ReYMeN" / "reports" / "tbench-plan-recovery.json")
```

#### I. tbench_test_runner.py — **KRİTİK**

| Satır | Bulunan Yol |
|-------|------------|
| 9 | `BASE = r"C:\\Users\\marko\\Desktop\\Reymen Proje\\ReYMeN-Ajan\\terminal-bench-benchmark\\original-tasks"` |
| 11 | `RESULTS_FILE = r"C:\\Users\\marko\\Desktop\\Reymen Proje\\.ReYMeN\\reports\\tbench-test-results.json"` |
| 160 | `report_path = r"C:\\Users\\marko\\Desktop\\Reymen Proje\\.ReYMeN\\reports\\tbench-test-report.md"` |

**Önerilen Düzeltme:** (tbench_plan_recovery.py ile aynı pattern)

### 2.3 scripts/ — (Git'te değil, legacy klasöründe)

| Dosya | Satır | Bulunan Yol |
|-------|-------|------------|
| scripts/start_bots.py | 5 | `BASE = Path(r"C:\\Users\\marko\\Desktop\\Reymen Proje\\ReYMeN-Ajan")` |
| scripts/tbench_plan_recovery.py | 10, 12 | Aynı absolute yollar |
| scripts/tbench_test_runner.py | 9, 11, 160 | Aynı absolute yollar |
| scripts/legacy/_github_plan.py | 5 | `KOK = r"C:\\Users\\marko\\Desktop\\Reymen Proje\\ReYMeN-Ajan"` |
| scripts/legacy/_yapi_analizi.py | 5 | `KOK = r"C:\\Users\\marko\\Desktop\\Reymen Proje\\ReYMeN-Ajan"` |

**Not:** Bu dosyalar `scripts/legacy/` dizininde olduğu için `.gitignore` tarafından zaten gizleniyor.

### 2.4 tests/ — Test Dosyaları (Orta Risk)

| Dosya | Satır | Bulunan Yol |
|-------|-------|------------|
| tests/test_browser_tool.py | 5 | `PROJE = r"C:\\Users\\marko\\Desktop\\Reymen Proje\\ReYMeN-Ajan"` |
| tests/test_standalone.py | 5 | `PROJE_KOK = r"C:\\Users\\marko\\Desktop\\Reymen Proje\\ReYMeN-Ajan"` |
| tests/_debug_pii.py | 3 | `sys.path.insert(0, r"C:\\Users\\marko\\Desktop\\Reymen Proje\\ReYMeN-Ajan")` |

**Önerilen Düzeltme:** `Path(__file__).parent.parent` ile değiştirilmeli.

### 2.5 legacy/, ReYMeN-memory-backup/ — (Zaten Git'te Değil)

ReYMeN-memory-backup/ içinde birçok dosya `C:\\Users\\marko\\OneDrive\\Desktop\\Reymen Proje\\hermes_projesi` yolunu kullanıyor. Bu dizinler .gitignore'da gizlendiği için sorun yok.

---

## 3. Bağımlılık Kontrolü

### 3.1 Mevcut requirements.txt (83 satır)

```
httpx>=0.27.0
openai>=1.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0
pyyaml>=6.0
requests>=2.31.0
python-telegram-bot>=20.0
duckduckgo_search>=6.0
mcp>=1.0.0
edge-tts>=6.0
pillow>=10.0.0
psutil>=5.9.0
numpy>=1.24.0
```

### 3.2 pyproject.toml Bağımlılıkları

pyproject.toml'da `[project.dependencies]` bölümü **YOK**. Sadece `hatchling` build sistemi tanımlı. Tüm bağımlılıklar `requirements.txt` üzerinden yönetiliyor.

### 3.3 Kodda Kullanılıp requirements.txt'te **AKTİF OLMAYAN** Kütüphaneler

| Kütüphane | Kullanıldığı Dosyalar | requirements.txt Durumu |
|-----------|----------------------|------------------------|
| **aiohttp** | 11 gateway dosyası (gateway_*.py) | ❌ **Yorum satırı** (`# aiohttp>=3.9.0`) |
| **fastapi** | api_server.py, web_ui/__init__.py, image_gen_route.py | ❌ **Yorum satırı** (`# fastapi>=0.100.0`) |
| **uvicorn** | web_ui/__init__.py, desktop/_server_daemon.py | ❌ **Yorum satırı** (`# uvicorn>=0.23.0`) |
| **starlette** | api_server.py | ❌ **Hiç yok** |
| **rich** | cli_main.py | ❌ **Yorum satırı** (`# rich>=13.0.0`) |
| **prompt_toolkit** | cli_helpers.py | ❌ **Yorum satırı** (`# prompt_toolkit>=3.0.0`) |
| **matrix-nio** | gateway_matrix.py | ❌ **Yorum satırı** (`# matrix-nio>=0.23.0`) |
| **pywin32** | desktop/tray.py (win32api, win32con, win32gui) | ❌ **Yorum satırı** (`# pywin32>=306`) |
| **docker** | tbench_quick5.py, tbench_sdk_runner.py | ❌ **Hiç yok** |
| **opencv-python** (cv2) | windows/nisan_yakala.py | ❌ **Hiç yok** |
| **keyboard** | windows/nisan_yakala.py | ❌ **Hiç yok** |
| **mss** | windows/nisan_yakala.py | ❌ **Hiç yok** |
| **fire** | sistem/mini_swe_runner.py | ❌ **Hiç yok** |
| **croniter** | (yorum satırında) | ❌ **Yorum satırı** (`# croniter>=2.0.0`) |
| **APScheduler** | (yorum satırında) | ❌ **Yorum satırı** (`# APScheduler>=3.10.0`) |
| **cryptography** | (yorum satırında) | ❌ **Yorum satırı** (`# cryptography>=41.0.0`) |

### 3.4 Güncellenmiş requirements.txt

```txt
# ─────────────────────────────────────────────────────────────────
# ReYMeN — Requirements (Güncellenmiş: 2026-07-02)
# Install: pip install -r requirements.txt
# Python >= 3.11 required
# ─────────────────────────────────────────────────────────────────

# === CORE (required) ===
httpx>=0.27.0
openai>=1.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0
pyyaml>=6.0
requests>=2.31.0

# === TELEGRAM GATEWAY ===
python-telegram-bot>=20.0

# === WEB SEARCH ===
duckduckgo_search>=6.0

# === MCP (Model Context Protocol) ===
mcp>=1.0.0

# === MEDIA & VISION ===
edge-tts>=6.0
pillow>=10.0.0

# === SCHEDULING ===
# croniter>=2.0.0          # İhtiyaç halinde aktifleştir
# APScheduler>=3.10.0

# === DATABASE ===
# SQLite3 (stdlib)

# === UTILITY ===
psutil>=5.9.0
numpy>=1.24.0

# === GATEWAYS (multi-platform) ===
aiohttp>=3.9.0             # 11 gateway modülü kullanıyor
# matrix-nio>=0.23.0       # Matrix gateway (opsiyonel)

# === WEB UI (gerekirse aktifleştir) ===
# fastapi>=0.100.0          # api_server.py + web_ui kullanıyor
# uvicorn>=0.23.0           # web_ui sunucusu
# starlette>=0.37.0         # api_server.py kullanıyor

# === CLI ===
# rich>=13.0.0              # cli_main.py kullanıyor
# prompt_toolkit>=3.0.0     # cli_helpers.py kullanıyor

# === WINDOWS AUTOMATION ===
# pywin32>=306              # desktop/tray.py kullanıyor
# opencv-python>=4.8.0      # windows/nisan_yakala.py (cv2)
# keyboard>=0.13.0          # windows/nisan_yakala.py
# mss>=9.0.0                # windows/nisan_yakala.py (ekran yakalama)

# === DEV / TEST ===
# docker>=7.0.0             # tbench scriptleri
# fire>=0.5.0               # mini_swe_runner.py
# pytest>=7.0.0
# pytest-asyncio>=0.23.0
```

### 3.5 Eksik Kütüphane Raporu

**Acil (kod çalışması için gerekli):**
1. **aiohttp** — 11 gateway modülü tarafından kullanılıyor, aktifleştirilmeli
2. **starlette** — `api_server.py` import ediyor ama hiç requirements'ta yok

**Orta (belirli özellikler için):**
3. **fastapi** — API sunucusu için (şu an yorum satırı)
4. **uvicorn** — Web UI sunucusu için (şu an yorum satırı)
5. **rich** — CLI deneyimi için (şu an yorum satırı)
6. **pywin32** — Windows system tray için (şu an yorum satırı)

**Düşük (özel scriptler):**
7. **docker** — tbench benchmark scriptleri
8. **opencv-python** — Windows ekran yakalama
9. **keyboard** — Windows klavye kontrolü
10. **mss** — Ekran görüntüsü yakalama
11. **fire** — CLI runner

---

## 4. Özet ve Öncelikli Eylemler

### Acil (Kod Çalışmasını Engeller)
1. **reymen/tbench_plan_recovery.py** — satır 10, 12: Absolute path'leri `Path(__file__)` ile değiştir
2. **reymen/tbench_test_runner.py** — satır 9, 11, 160: Absolute path'leri `Path(__file__)` ile değiştir

### Yüksek Öncelik
3. **src/reymen/windows/tor_otomasyonu.py** — satır 82-86: Hardcoded Tor Browser yolları dinamik hale getirilmeli
4. **tests/test_browser_tool.py, test_standalone.py, _debug_pii.py** — Absolute path'ler düzeltilmeli

### Orta Öncelik
5. **src/reymen/guvenlik/file_safety.py** — `C:\\Windows` → `os.environ.get('SystemRoot')`
6. **src/reymen/guvenlik/network_restriction.py** — `C:\\Windows` → `os.environ.get('SystemRoot')`
7. **src/reymen/tools/obsidian_tool.py** — Docstring'lerde `marko` → `kullanici`

### Düşük Öncelik
8. **src/reymen/platform_adapter.py, container_sandbox.py** — Docstring'lerdeki `marko` referansları
9. **`.env.example`** — Oluşturulması önerilir
10. **requirements.txt** — `aiohttp` ve `starlette` aktifleştirilmeli

---

## 5. GitHub Push Bilgisi

Bu rapor `rapor/mutlak_yol_raporu.md` dosyasına kaydedildi.

**Not:** `rapor/` dizini `.gitignore`'a **eklenmemiş**. Eğer push yapılacaksa:
- Ya `rapor/` .gitignore'a eklenir
- Ya da rapor geçici olarak alınıp push sonrası silinir

Mevcut .gitignore'da `reports/` var ama `rapor/` (Türkçe) yok.
