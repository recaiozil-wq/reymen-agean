---
name: software-development_reymen-proje-mimarisi_references_hermes-reference-test-fix-patterns
description: Hermes Reference Test Fix Patterns
title: "Software Development Reymen Proje Mimarisi References Hermes Reference Test Fix Patterns"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Hermes Reference Test Fix Patterns |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Hermes Reference Test Fix Patterns

Reymen projesinde Hermes'ten kopyalanan referans testleri (`tests/hermes_reference/`) çalıştırırken karşılaşılan yaygın hatalar ve çözümleri.

## 1. session_db.py — Eksik Metodlar

**Hata:** `AttributeError: 'SessionDB' object has no attribute 'set_session_archived'`

**Çözüm:** `ReYMeN_state.py`'de SessionDB sınıfına ekle:

```python
def set_session_archived(self, session_id: str, archived: bool) -> bool:
    """Set the archived flag. For compression pairs, also updates the parent chain."""
    val = 1 if archived else 0
    def _do(conn):
        cursor = conn.execute(
            "UPDATE sessions SET archived = ? WHERE id = ?", (val, session_id))
        if cursor.rowcount == 0:
            return 0
        # Update compression parent too
        row = conn.execute(
            "SELECT parent_session_id FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if row and row["parent_session_id"]:
            parent = conn.execute(
                "SELECT end_reason FROM sessions WHERE id = ?",
                (row["parent_session_id"]),
            ).fetchone()
            if parent and parent["end_reason"] == "compression":
                conn.execute(
                    "UPDATE sessions SET archived = ? WHERE id = ?",
                    (val, row["parent_session_id"]))
        return cursor.rowcount
    return self._execute_write(_do) > 0
```

**Ayrıca:** SCHEMA_SQL'de sessions tablosuna `archived INTEGER NOT NULL DEFAULT 0` kolonu ekle. `list_sessions_rich()`'e `archived_only` parametresi ekle (varsayılan `False` = archived olmayanları göster).

## 2. openviking URI — Eksik Agent Segmenti

**Hata:** URI'de `/agent/` segmenti yok
- Beklenen: `viking://user/alice/agent/coder/memories/preferences/mem_...`
- Mevcut: `viking://user/alice/memories/preferences/mem_...`

**Çözüm:** `plugins/memory/openviking/__init__.py`'de `_build_memory_uri()`'yi güncelle:

```python
return f"viking://user/{self._user}/agent/{self._agent}/memories/{subdir}/mem_{slug}.md"
```

## 3. website Scriptleri — Path ve İçerik Farkı

**Hata 1:** `FileNotFoundError: tests/website/scripts/extract-skills.py`
**Çözüm:** `website/scripts/extract-skills.py`'yi `tests/website/scripts/`'e kopyala (veya symlink).

**Hata 2:** `module 'extract_skills' has no attribute '_source_url'`
**Çözüm:** `extract-skills.py`'ye `_source_url()` fonksiyonunu TAG_TO_CATEGORY bloğundan sonra ekle:

```python
def _source_url(source: str, identifier: str, extra: dict) -> str:
    """Build clickable source URL for a skill."""
    detail = extra.get("detail_url") or extra.get("source_url")
    if detail:
        return detail
    source = source.lower().replace("_", "-")
    if source == "github":
        parts = identifier.split("/", 2)
        if len(parts) == 3:
            return f"https://github.com/{parts[0]}/{parts[1]}/tree/main/{parts[2]}"
        elif len(parts) == 2:
            return f"https://github.com/{parts[0]}/{parts[1]}"
        return ""
    if source == "clawhub":
        return f"https://clawhub.ai/skills/{identifier.removeprefix('clawhub/')}"
    if source == "lobehub":
        return f"https://lobehub.com/agent/{identifier.removeprefix('lobehub/')}"
    if source in ("browse-sh", "browse.sh"):
        return extra.get("source_url", "")
    if source in ("skills-sh", "skills.sh"):
        return f"https://skills.sh/{identifier.removeprefix('skills-sh/')}"
    return ""
```

**Hata 3:** `assert 'crypto' == 'blockchain'` ve junk tag filtreleme
**Çözüm:** TAG_TO_CATEGORY'e ek mapping'ler ekle:
- `"blockchain": ["crypto", "blockchain", "web3"]`
- `"communication": ["communication", "chat", "messaging"]`
- `"apple": ["apple", "ios", "macos"]`
- `"automation": ["automation", "workflow"]`

Ve `_guess_category()`'de junk tag filtresi:

```python
first = tags[0] if isinstance(tags[0], str) else ""
if first:
    import re
    if re.search(r'\d+\.\d+', first) or re.search(r'^[A-Z][a-z]+\d', first) or re.search(r'^[A-Z][a-z]+ [A-Z]', first):
        return "uncategorized"
return first.lower().replace(" ", "-") if first else "uncategorized"
```

## 4. Test Fix Workflow

1. **Collection check:** Her kategoriyi ayrı ayrı `--collect-only` ile dene
2. **Çalışan kategoriler:** `--tb=short -q` ile koş, hataları kategorize et
3. **Basit fix:** Eksik metod/import/fonksiyon varsa direkt ekle
4. **Karmaşık fix:** Collection error (Hermes import'ları) → Claude Code'a task olarak ver
5. **Doğrulama:** Fix sonrası kategoriyi tekrar koş, tüm testler geçene kadar tekrarla

## 5. Silinen/Değiştirilen Dosyayı Kurtarma

extract-skills.py gibi büyük dosyalarda patch hataları girintiyi bozabilir. Çözüm:
- Backup al: `cp file.py file.py.bak`
- Bozulursa: `tests/website/scripts/extract-skills.py` orijinal kopyasını `website/scripts/`'e kopyala (test kopyası ilk cp'den bozulmamıştır)
