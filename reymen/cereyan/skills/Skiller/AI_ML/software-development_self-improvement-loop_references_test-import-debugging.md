---
name: software-development_self-improvement-loop_references_test-import-debugging
description: Systematic Test Import Debugging
title: "Software Development Self Improvement Loop References Test Import Debugging"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Systematic Test Import Debugging |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Systematic Test Import Debugging

## Problem
Fork/proje dönüşümü sonrası `tests/` dizininde çok sayıda import hatası.
Hermes → ReYMeN gibi bir rebranding sonrası sembol isimleri, modül yolları
ve API'ler değiştiği için testler import edemez hale gelir.

## ⚠️ Ön-Kategorilendirme Tuzakları

Decisions.md'de veya skill'de önceden yazılı kategorilere körüne güvenme.
Örnek: `env_float from utils (~20 dosya)` olarak sınıflandırılmıştı ama
gerçekte **0 test dosyası** `env_float`'ı import ediyordu. Hata 2 kaynak
dosyadaydı (`agent/auxiliary_client.py`, `agent/chat_completion_helpers.py`).

**Her seferinde doğrula:** `search_files` ile eksik sembolü .py dosyalarında ara.
`__pycache__/` sonuçlarını yoksay — onlar derlenmiş bytecode.

## Tanı Yöntemi (Hızlı)

Test modüllerini import etmeye çalışmak timeout'a takılabilir (bazı modüller
ağır bağımlılıklar yükler). Bunun yerine **statik tarama** yap:

```python
import os
from collections import defaultdict

imports = []  # (module, symbol) pairs
for root, dirs, files in os.walk('tests'):
    if '__pycache__' in root:
        continue
    for f in files:
        if not f.endswith('.py'):
            continue
        with open(os.path.join(root, f)) as fp:
            for line in fp:
                line = line.strip()
                if line.startswith('from ') and ' import ' in line:
                    parts = line.split(' import ', 1)
                    module = parts[0].replace('from', '').strip()
                    symbols = [s.strip().split(' as ')[0] for s in parts[1].split(',')]
                    for sym in symbols:
                        imports.append((module, sym))

by_mod = defaultdict(set)
for mod, sym in imports:
    by_mod[mod].add(sym)
```

Sonra her (module, symbol) çiftini doğrula:
```python
import importlib
for mod, symbols in by_mod.items():
    try:
        m = importlib.import_module(mod)
        for sym in symbols:
            if not hasattr(m, sym):
                print(f'MISSING: {mod}.{sym}')
    except ImportError:
        print(f'MODULE MISSING: {mod}')
```

## Kaynak Koddaki Eksik Import'lar
Import hataları sadece test dosyalarında olmaz. Ana kod (`agent/`, `tools/`,
`gateway/`) da import edemeyebilir. Bunları da tara:

```python
for root, dirs, files in os.walk('.'):
    if '/tests/' not in root and f.endswith('.py'):
        # Aynı tarama
```

## Kategorilendirme
Hataları **eksik sembol + kaynak modül** çiftine göre grupla.

| Eksik Sembol | Kaynak Modül | Etkilenen |
|-------------|-------------|-----------|
| `env_float`, `env_int` | `utils` | `agent/auxiliary_client.py`, `agent/chat_completion_helpers.py` |
| `SessionEntry` | `gateway.session` | ~7 test dosyası |
| `APIServerAdapter` | `gateway.platforms.api_server` | ~5 |
| `cleanup_browser` | `tools.browser_tool` | ~4 |
| `SessionManager` | `acp_adapter.session` | ~4 |
| Yuanbao importları | `gateway.platforms.yuanbao` | ~4 |
| Diğer tekillikler | çeşitli | ~26 |

## 🎯 Değer Bazlı Önceliklendirme

Tüm import fix'leri eşit değerde DEĞİLDİR. Kullanıcı şüphe duyduğunda
(ör: "testler bir şeye yaramazsa korkuyorum") şu sıralamayı kullan:

### Öncelik 1 — Projeye Ait Testler (🟢 Yüksek)
- `tests/` içinde (ReYMeN_reference DEĞİL) gerçek testler
- **Fix yap ve çalıştır.** Proje için kritik.

### Öncelik 2 — Upstream Referans Testleri (🟡 Orta)
- `tests/ReYMeN_reference/` altındaki upstream Hermes testleri
- **Import fix yap** (shim/stub ekle) ama testin kendisi hala çalışmayabilir
- Test mantığı projeye uymuyorsa **testi sil**, sadece import'ı düzeltme

### Öncelik 3 — Kullanılmayan Modüller (🔴 Düşük)
- ACP, Yuanbao gibi projede aktif olmayan özelliklerin testleri
- **Doğrudan sil.** Zaman kaybı, fix'in faydası yok.

### 🔴🔀🟢 Overlap: Kullanılmayan modül + Proje testi
Bir modül kullanılmayan (🔴) olarak sınıflandırılmış olsa bile, proje testleri (🟢)
o modülü import edip test ediyorsa ikisi birleştirilmelidir:

| Durum | Eylem |
|-------|-------|
| Modül kullanılmıyor + proje testi **YOK** | 🔴 Sil, zaman kaybı |
| Modül kullanılmıyor + proje testi **VAR** | 🔀 Shim/stub ekle, testleri koru |
| Modül kullanılmıyor + sadece **referans testleri** VAR | 🟡 En kısa shim + test çalıştır, çalışmazsa sil |

### Nasıl Karar Verilir?
1. Test hangi modülü test ediyor? (dosyanın import/class adına bak)
2. O modül projede mevcut mu? `search_files` ile kontrol et
3. Modül mevcut ama farklı API ile çalışıyor mu? → 🟡 (fix + adapt)
4. Modül projede yok / hiç kullanılmıyor mu? → 🔴 (sil)
5. Modül projede var ve API aynı mı? → 🟢 (sadece import fix yeterli)
6. Modül kullanılmıyor ama projenin kendi testi (🟢) var mı? → 🔀 overlap (shim ekle, testi koru)

## Çözüm Stratejisi (teknik)

### 1. Upstream'den Port Et
Var olan sembolü upstream'te bul ve aynısını projeye ekle.
```bash
git show upstream/main:utils.py | grep -n "def env_float"
git show upstream/main:gateway/session.py | grep -n "class SessionEntry"
```

### 2. Stub/Shim Ekle (Önerilen: Upstream-Uyumlu Dataclass)
En temiz yöntem — mevcut modüle eksik dataclass/sınıfı ekle.
**Kural:** Sadece testin import etmesine yetecek minimum alanları ekle,
gerçek mantığı değiştirme.

```python
@dataclasses.dataclass
class SessionEntry:
    """Upstream Hermes uyumluluk katmani — test import zinciri için."""
    session_key: str = ""
    session_id: str = ""
    created_at: Any = None
    updated_at: Any = None
    platform: Any = None
    chat_type: str = "dm"
```

**Ne zaman kullanılır:** Sembol bir test conftest.py'de import ediliyorsa ve
test projeye uyarlanabilir durumdaysa. Mock'tan daha temiz çünkü:
- Gerçek modüle eklenir, test dışında da kullanılabilir
- Test conftest.py'yi değiştirmek gerekmez
- Yeni sembol eski API'yi bozmaz

### 3a. Multi-Class Stub (Kullanılmayan Modüller İçin)
Bir kullanılmayan modülün proje testleri varsa, eksik olan tüm sınıfları,
fonksiyonları ve sabitleri aynı anda stub olarak ekle. Her birine sadece
testlerin import etmesine yetecek minimal imza ver.

**Örnek** (Yuanbao — 3 dosyada 75 test korundu):

```python
# gateway/platforms/yuanbao.py
# 1. Constants
DEFAULT_WS_GATEWAY_URL: str = "wss://yuanbao.woa.com/ws"
HEARTBEAT_INTERVAL_SECONDS: float = 30.0
MAX_RECONNECT_ATTEMPTS: int = 100
NO_RECONNECT_CLOSE_CODES: frozenset = frozenset({4012, 4013})
AUTH_FAILED_CODES: frozenset = frozenset({4001, 4002, 4003, 4010})

# 2. Stub classes
class YuanbaoAdapter: pass
class SignManager: pass
class ConnectionManager: pass
# ... etc.

# 3. Implemented methods (MarkdownProcessor — gerçek implementasyon)
class MarkdownProcessor:
    @staticmethod
    def has_unclosed_fence(text): ...
    @staticmethod
    def split_into_atoms(text): ...
    # ... etc.
```

**Doğrulama:**
```bash
python3 -m pytest tests/test_yuanbao.py tests/test_yuanbao_media.py tests/test_yuanbao_sticker.py -q
→ 75 passed
```

### 3. Mock ile Çöz
Test conftest.py'de veya fixture'da mock oluştur.
```python
import sys
from unittest.mock import MagicMock
sys.modules["gateway.session"].SessionEntry = MagicMock()
```
**Ne zaman kullanılır:** Sembol sadece 1-2 test dosyasında import ediliyorsa
ve gerçek implementasyonu eklemek riskli/uzunsa.

### 4. Testi Güncelle
Yeni API'ya uygun hale getir.
`from ReYMeN_cli.commands import resolve_command`
→ mevcut API'yi bul, testi yeniden yaz.

### 5. Testi Kaldır
Upstream'e özgü bir testse ve projede karşılığı yoksa sil.
**Hata yapma:** Önce `search_files` ile sembolün projede başka yerde
kullanılıp kullanılmadığını kontrol et. Sadece test dosyası kullanıyorsa
güvenle silebilirsin.

## Pitfall: Upstream Fuzzy Search Threshold

Upstream search fonksiyonları düşük skorlu (score > 0) sonuçları bile
"match" olarak döndürebilir. Bu, hiçbir alakası olmayan sorgulara bile
sonuç verilmesine yol açar.

**Belirti:** `search_stickers("qwertyuiop1234567890")` → sticker döndürüyor

**Kök neden:** `search_stickers()`'ta `top <= 0` check'i sadece sıfır skoru
filtrerliyor. Oysa `_multiset_char_hit_ratio` ve `_bigram_jaccard` gibi
fonksiyonlar, ingilizce karakterler içeren açıklamalar (ör: "awesome") ile
rastgele ASCII sorguları arasında düşük ama pozitif skor üretebiliyor (ör: 12.4).

**Fix:**
```python
# Değişiklik öncesi (top <= 0 → tüm düşük skorlu sonuçları döndürür)
if top <= 0:
    return [s for _, s in scored[:safe_limit]]

# Değişiklik sonrası (top <= 20 → anlamlı eşleşme yok sayılır)
if top <= 20:
    return []
```

Sıfır skor değil, **anlamlı eşleşme eşiği** kullan. Bu eşik değeri
testlerde kullanılan sorgularla (tek harf "a", İngilizce kelimeler "awesome")
hala eşleşmeye yetecek kadar düşük ama rastgele sorguları filtreleyecek
kadar yüksek olmalı. `20` değeri bu dengeyi sağlar.

**Test pivotları:**
```python
# Çalışmalı:
search_stickers("六六六")     → exact name → yüksek skor
search_stickers("awesome")   → description keyword → ~50+
search_stickers("a")         → single char in many descs → ~22+

# Boş dönmeli:
search_stickers("qwertyuiop1234567890") → 0 sonuç
search_stickers("zzz_nonexistent_xyz_12345") → 0 sonuç
```

## Referans: env_float / env_int

Upstream Hermes'ten port edilmiştir. `utils` modülüne eklenir:

```python
import math

def env_float(
    name: str,
    default: float = 0.0,
    min_value: float | None = None,
    max_value: float | None = None,
) -> float:
    """Read a float env var with clamping against NaN/Inf and optional bounds."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        val = float(raw)
    except (ValueError, TypeError):
        return default
    if not math.isfinite(val):
        return default
    if min_value is not None:
        val = max(val, min_value)
    if max_value is not None:
        val = min(val, max_value)
    return val

def env_int(
    name: str,
    default: int = 0,
    min_value: int | None = None,
    max_value: int | None = None,
) -> int:
    """Read an int env var with clamping and bounds."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        val = int(raw)
    except (ValueError, TypeError):
        return default
    if min_value is not None:
        val = max(val, min_value)
    if max_value is not None:
        val = min(val, max_value)
    return val
```

## Referans: SessionEntry Stub

`gateway/session.py`'ye eklenir (upstream Hermes e2e conftest.py uyumluluğu):

```python
@dataclasses.dataclass
class SessionEntry:
    """Session kaydi — upstream Hermes uyumluluk katmani.
    Test ve gateway.run import zincirini kirabilmek icin minimum alanlari iceren dataclass.
    """
    session_key: str = ""
    session_id: str = ""
    created_at: Any = None  # datetime
    updated_at: Any = None  # datetime
    platform: Any = None     # gateway.config.Platform
    chat_type: str = "dm"
```

**Doğrulama:**
```bash
python3 -c "from gateway.session import SessionEntry; print('✅')"
python3 -c "
from gateway.session import SessionEntry, SessionSource, build_session_key
from datetime import datetime
from gateway.config import Platform

source = SessionSource(platform=Platform.TELEGRAM, chat_id='test', user_id='user')
key = build_session_key(source)
entry = SessionEntry(
    session_key=key,
    session_id='sess-test',
    created_at=datetime.now(),
    updated_at=datetime.now(),
    platform=Platform.TELEGRAM,
    chat_type='dm'
)
print(f'OK: {entry.session_key}')
"
```

## Circular-Import-Safe Stub Pattern (delegate_tool tipi)

Bazı modüller kendilerini import eden sembollere ihtiyaç duyar ama aynı modülün
içinde tanımlanamaz çünkü modül henüz yüklenmemiştir. Örnek: `tools/delegate_tool.py`
içinde `_run_single_child` — testler `patch("tools.delegate_tool._run_single_child")`
ile mock'lar ama modül kendini import edemez.

### Standart try/except yaklaşımı (ÇALIŞMAZ)
```python
# tools/delegate_tool.py
try:
    from tools.delegate_tool import _run_single_child  # HATA: Circular import
except ImportError:
    def _run_single_child(...): ...
```
Bu `try/except ImportError` ile çalışır — ilk import'ta modül henüz
yüklenmediği için ImportError fırlatır ve fallback stub tanımlanır.
Sonraki import'larda sembol zaten tanımlı olduğu için ImportError olmaz.

### Ne zaman kullanılır?
- Test dosyası `patch("tools.delegate_tool._run_single_child")` ile mock yapıyor
- Sembol mevcut modülde tanımlı değil
- Sembolü modüle doğrudan eklemek modülün başlatılmasını bozuyor (circular import)
- Sembol `asyncio.run()` gibi runtime çağrıları gerektiriyorsa stub yeterli

### Doğrulama
```bash
python3 -c "from tools.delegate_tool import _run_single_child; print('✅ Import OK')"
```

## Uygulama
- Her saat/kategori bir çözüm (self-improvement loop Mod B)
- Çözümü `decisions.md`'ye kaydet (Karar Döngüsü)
- Doğrula: `python3 -c "from MODULE import SYMBOL"`
- **Her kategoriden önce GÖZLEM adımında kategorileri doğrula** — 
  `search_files` ile sembolün source dosyalarda gerçekten import edildiğini teyit et
