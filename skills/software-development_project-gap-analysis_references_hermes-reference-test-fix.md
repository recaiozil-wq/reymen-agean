---
name: software-development_project-gap-analysis_references_hermes-reference-test-fix
description: Hermes Reference Test Hata Düzeltme Pattern'leri
title: "Software Development Project Gap Analysis References Hermes Reference Test Fix"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Hermes Reference Test Hata Düzeltme Pattern'leri |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Hermes Reference Test Hata Düzeltme Pattern'leri

Bir projeyi (örn: ReYMeN) Hermes Agent seviyesine çıkarırken `tests/hermes_reference/` içindeki testlerin geçmesi gerekir. Bu referans dosyası, karşılaşılan hata türleri ve çözüm pattern'lerini belgeler.

## 1. Collection Error Cascade — Kategorilere Ayırarak Koş

**Sorun:** Tüm `tests/hermes_reference/` tek seferde pytest'e verildiğinde, bir kategorideki collection error tüm suite'i bloke eder.

```
collected 379 items / 373 errors / 6 skipped
```

**Çözüm:** Kategorileri ayrı ayrı koş:

```bash
# Önce collection error'u olmayan kategorileri bul
for cat in hermes_state openviking_plugin cron website; do
    python -m pytest tests/hermes_reference/$cat/ --collect-only 2>&1 | grep "collected\|ERROR"
done

# Sonra çalışanları koş
python -m pytest tests/hermes_reference/hermes_state/ --tb=short -q
python -m pytest tests/hermes_reference/openviking_plugin/ --tb=short -q
```

**Kategori bazında koleksiyon yap:**
```bash
# ERROR sayısı 0 olan kategoriler = çalışan
# ERROR sayısı > 0 olanlar = collection error düzeltmesi gerek
python -m pytest tests/hermes_reference/ --collect-only 2>&1 | grep "^ERROR " | sort | uniq -c | sort -rn
```

## 2. Eksik Schema Kolonu — SCHEMA_SQL'e Ekle

**Sorun:** `'SessionDB' object has no attribute 'set_session_archived'`

**Çözüm:** 
```python
# 1. SCHEMA_SQL'e kolon ekle (otomatik migrate olur)
archived INTEGER NOT NULL DEFAULT 0,

# 2. Metodu ekle
def set_session_archived(self, session_id: str, archived: bool) -> bool:
    val = 1 if archived else 0
    def _do(conn):
        cursor = conn.execute(
            "UPDATE sessions SET archived = ? WHERE id = ?", (val, session_id)
        )
        ...
    return self._execute_write(_do) > 0

# 3. list_sessions_rich'e parametre ekle
def list_sessions_rich(self, ..., archived_only: bool = False):
    if archived_only:
        where_clauses.append("s.archived = 1")
    else:
        where_clauses.append("COALESCE(s.archived, 0) = 0")
```

**Sistem zaten `_reconcile_columns()` ile otomatik migrate eder** — SCHEMA_SQL'e kolon eklemek yeterli.

## 3. Eksik Script Dosyaları — Doğru Yola Kopyala

**Sorun:** Test `parents[2]` ile proje köküne gider ama Hermes test yapısında bu `tests/` dizinine denk gelir.

```
GENERATOR = REPO_ROOT / "website" / "scripts" / "generate-skill-docs.py"
# parents[2] = tests/ → tests/website/scripts/generate-skill-docs.py (YANLIŞ)
# Gerçek:    website/scripts/generate-skill-docs.py (DOĞRU)
```

**Çözüm:** Script'leri testin beklediği yere kopyala:
```bash
mkdir -p tests/website/scripts
cp website/scripts/extract-skills.py tests/website/scripts/
cp website/scripts/generate-skill-docs.py tests/website/scripts/
```

**Alternatif:** Test'teki `REPO_ROOT`'u `parents[2]` → `parents[3]` yap (ama Hermes referans testleri değişirse tekrar eski haline döner).

## 4. Eksik Import / Fonksiyon — Modüle Ekle

**Sorun:** `ImportError: cannot import name 'model_forces_max_completion_tokens' from 'utils'`

**Çözüm:** 
1. İlgili modülde fonksiyon gerçekten var mı kontrol et (`grep -n "def model_forces" utils.py`)
2. Yoksa Hermes'teki referans implementasyonu bul (`tests/hermes_reference/` içinde arama yap)
3. Eksik fonksiyonu taşı/yaz
4. `python -c "from utils import model_forces_max_completion_tokens; print('OK')"` ile doğrula

## 5. İçerik Farkı — `_guess_category()` Gibi Fonksiyonlar

**Sorun:** Aynı fonksiyon var ama farklı mapping kullanıyor
```
assert mod._guess_category(["crypto"]) == "blockchain"
# Reymen'de dönen: 'crypto'
```

**Çözüm:** 
- Bu kod değişikliği gerektirir (Claude Code'a ver)
- Eğer Reymen'in kendi mapping'i kasıtlıysa, test'i güncelle (Hermes sync'te kaybolur)
- Eğer Hermes'teki mapping daha doğruysa, Reymen'in fonksiyonunu güncelle

## 6. Cron Import Path Sorunu

**Sorun:** Hermes testleri `from cron.suggestions import ...` yapar ama Reymen'de `ReYMeN_cli/cron/suggestions.py`

**Çözüm (geçici):**
```python
# __init__.py veya conftest.py'ye ekle
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "ReYMeN_cli"))
```

**Çözüm (kalıcı):** Import'ları `from ReYMeN_cli.cron import ...` olarak değiştir.

## 7. Özet Tablo Formatı

Her düzeltme adımından sonra şu formatla rapor ver:

```
| Kategori | Önce | Sonra |
|----------|------|-------|
| hermes_state | 2 ❌ | 33/33 ✅ |
| openviking | 2 ❌ | 13/13 ✅ |
| website | 20 ERROR | 10 ✅ / 10 ❌ |
```

Kullanıcının Claude Code'a vermesi için:
```
**OZET:** hermes_state=2fix, openviking=2fix, website=20fix(yeni script), cron=192fix(import+path+metod)
```
