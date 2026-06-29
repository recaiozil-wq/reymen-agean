---
name: software-development_fork-project-audit_references_hermes-reference-test-fix-17-haziran-2026
description: Hermes Reference Test Fix — 17 Haziran 2026 Oturumu
title: "Software Development Fork Project Audit References Hermes Reference Test Fix 17 Haziran 2026"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Hermes Reference Test Fix — 17 Haziran 2026 Oturumu |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Hermes Reference Test Fix — 17 Haziran 2026 Oturumu

## Genel Durum

Reymen projesinde 1.555 Hermes reference test dosyasi tarandi.
25 kategoriden 4'u calisabildi, 12'si collection error (import), gerisi destek.

## Duzeltilenler

### 1. hermes_state (2 hata -> 33/33)

**Dosya:** `ReYMeN_state.py` (SessionDB sinifi)

**Degisiklikler:**
- SCHEMA_SQL'e `archived INTEGER NOT NULL DEFAULT 0` kolonu eklendi
- `_reconcile_columns()` sayesinde startup'ta otomatik olusur
- `set_session_archived(session_id, archived)` metodu eklendi:
  - Session'in archived kolonunu gunceller (0 veya 1)
  - Compression parent chain'deki root session'i da gunceller
  - `_execute_write(_do)` pattern'i ile yazilir
- `list_sessions_rich()`'e `archived_only=False` parametresi eklendi
  - Varsayilan: `archived = 0` olanlari goster
  - `archived_only=True`: sadece archived olanlari goster
- `get_session()` zaten `SELECT *` yaptigi icin yeni kolon otomatik gelir

### 2. openviking_plugin (2 hata -> 13/13)

**Dosya:** `plugins/memory/openviking/__init__.py`

**Degisiklik:**
- `_build_memory_uri()`'de URI formatina `/agent/{self._agent}/` segmenti eklendi
- Eski: `viking://user/{user}/memories/{subdir}/mem_{slug}.md`
- Yeni: `viking://user/{user}/agent/{agent}/memories/{subdir}/mem_{slug}.md`

### 3. website (20 ERROR -> 20/20)

**Sorun:** Test `REPO_ROOT = Path(__file__).resolve().parents[2]` ile
`tests/` dizinine gidiyor, script'leri `tests/website/scripts/`'te ariyor.
Ama script'ler asil proje kokunde `website/scripts/`'te.

**Cozum:** `tests/website/scripts/` klasoru olusturulup script'ler kopyalandi.
Ayrica script'lere 2 fonksiyon eklendi:

**`_source_url(source, identifier, extra)` — yeni fonksiyon:**
- Github, ClawHub, LobeHub, browse.sh, skills.sh kaynaklarindan URL sentezler
- `extra["detail_url"]` veya `extra["source_url"]` varsa oncelikli kullanir

**`_guess_category()` — junk tag detektoru eklendi:**
- Versiyon stringi (`0.10.7-dev`) -> "uncategorized"
- Brand name (`Doramagic Crystal`) -> "uncategorized"
- Karisik (`Ap2`) -> "uncategorized"
- Regex: `\d+\.\d+`, `^[A-Z][a-z]+\d`, `^[A-Z][a-z]+ [A-Z]`

**TAG_TO_CATEGORY mapping'ine eklendi:**
- `blockchain: ["crypto", "blockchain", "web3"]`
- `communication: ["communication", "chat", "messaging"]`
- `apple: ["apple", "ios", "macos"]`
- `automation: ["automation", "workflow"]`

## Kalan Hatalar (Claude Code'a devredilecek)

| Kategori | Hata | Sebep |
|----------|------|-------|
| cron | 100 FAIL + 92 ERROR | import path + runtime_provider + scheduler |
| hermes_cli | 131 collection error | Hermes CLI import'lari |
| agent | 45 | agent.transports, lsp |
| cli | 35 | Hermes CLI yapisi |
| plugins | 21 | memory/image_gen/video_gen eklentileri |
| run_agent | 56 | agent_guardrails, compression |
| acp | 10 | acp_adapter.auth import |
| docker | 6 | Docker modulleri yok |
| providers | 4 | provider profil import |
| integration | 4 | modal_terminal, ha |
| e2e | 2 | gateway.platforms.base |
| acp_adapter | 2 | acp_adapter import |
| gateway | 171 | gateway.platforms, session |
| honcho_plugin | 5 | honcho_plugin import |

## Onemli Desenler

1. **Toplu kosma -> bloke:** Collection error'lar tum suite'i bloke eder.
   Her kategoriyi AYRI kos.

2. **parents[2] tuzagi:** Test'in `REPO_ROOT` hesaplamasi Hermes'te dogru,
   Reymen'de yanlis dizine gider. Her zaman kontrol et.

3. **`SELECT *` avantaji:** `get_session()` gibi `SELECT *` kullanan metodlar
   yeni kolonlari otomatik icerir. Ek is gerekmez.

4. **`_reconcile_columns()`:** SCHEMA_SQL'e kolon eklemek yeterli.
   Startup'ta otomatik ALTER TABLE ADD COLUMN yapar.
