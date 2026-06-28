---
name: software-development_fork-project-audit_references_hermes-reference-test-fix
description: Hermes Reference Test Fix Workflow
title: "Software Development Fork Project Audit References Hermes Reference Test Fix"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Hermes Reference Test Fix Workflow |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Hermes Reference Test Fix Workflow

Bir fork'ta (ör: ReYMeN) Hermes reference testlerini düzeltirken izlenecek
sistematik yaklaşım.

## Adımlar

### 1. Kategorileri Tek Tek Koş

Tümünü birden koşma — collection error'lar kaskat bloke eder.

```bash
# Her kategoriyi ayrı koş:
python -m pytest tests/hermes_reference/<kategori>/ --tb=short -q 2>&1 | tail -3

# Önce collect-only ile durumu gör:
python -m pytest tests/hermes_reference/<kategori>/ --collect-only 2>&1 | grep "collected\|ERROR"
```

### 2. Kategorilendir

| Durum | Ne yapmalı |
|-------|-----------|
| collection error (ImportError/ModuleNotFoundError) | Kod import'u gerektirir → Claude Code'a devret |
| test FAILED (assertion) | Küçük kod/veri düzeltmesi → direkt yapılabilir |
| test ERROR (setup fixture) | Genellikle path/metod eksik → direkt düzeltilebilir |

### 3. Doğrudan Düzeltilebilir Hatalar

**Schema/metod ekleme:** `SELECT * FROM sessions` ile çalışan `get_session()`'a
yeni kolon otomatik gelir. `_reconcile_columns()` varsa SCHEMA_SQL'e kolon
eklemek yeterli — startup'ta kendiliğinden oluşur.

**Import edilebilir metodlar:**
- Sınıfa yeni metod ekle (mevcut pattern'i kopyala: `_execute_write(_do)`)
- Test'in beklediği davranışı test'ten oku (parametreler, return değeri, yan etkiler)

**Eksik script'ler:**
- Test `importlib.util.spec_from_file_location()` ile script yükler
- Script mevcutsa ama path farklıysa: ya script'i beklendiği yere kopyala
  ya da test'in REPO_ROOT hesaplamasını kontrol et

### 4. Claude Code'a Devredilecek Hatalar

Şu durumlarda task description hazırla:

- **Import path farkı:** `from cron.suggestions` → `from ReYMeN_cli.cron.suggestions`
- **Hermes'e özel fonksiyon:** `format_runtime_provider_error`, `model_forces_max_completion_tokens`
- **Hermes modülü:** `gateway.platforms.base`, `acp_adapter.auth`, `agent.transports`
- **Yapısal fark:** scheduler, profil yönetimi, workdir çözümlemesi

Task description formatı:
```
GOREV: [tek cümle]
Konum: [tam yol]
Dosya: [hangisi]
Hata: [hata mesajı]
Cozum: [ne yapılmalı]
```

### 5. Doğrulama

```bash
# Her düzeltme sonrası ilgili kategoriyi koş
python -m pytest tests/hermes_reference/<kategori>/ --tb=short -q 2>&1 | tail -3

# Önce/sonra karşılaştırması yap
echo "Once: N failed -> Sonra: 0 failed"
```

## Pitfalls

- **Toplu koşma:** collection error'lar diğer kategorileri bloke eder.
  Her kategoriyi AYRI koş.
- **Test script path'i:** `REPO_ROOT = Path(__file__).resolve().parents[2]` 
  farklı proje yapısında yanlış dizine gidebilir — kontrol et.
- **get_session SELECT *:** Yeni kolon eklediysen `get_session` zaten içerir.
- **collection error ≠ 0 test:** Bazı test'ler conftest.py'deki tek bir import
  yüzünden bloke olur — o import düzelince tüm kategori açılır.
