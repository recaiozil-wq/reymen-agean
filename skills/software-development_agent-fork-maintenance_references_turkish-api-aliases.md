---
name: software-development_agent-fork-maintenance_references_turkish-api-aliases
description: Turkish API Alias Pattern
title: "Software Development Agent Fork Maintenance References Turkish Api Aliases"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Turkish API Alias Pattern |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Turkish API Alias Pattern

## Problem

ReYMeN fork uses English command names internally, but ReYMeN-specific tests and user-facing integrations expect Turkish (or vice versa). Maintaining two separate APIs is brittle.

## Solution

Add a lightweight dictionary alias at the top of the `run()` (or equivalent) function:

```python
def run(islem: str = "", **kwargs) -> str:
    # Türkçe → İngilizce alias mapping
    _alias = {
        "ac": "navigate",        # aç → navigate
        "kapat": "back",         # kapat → back
        "git": "navigate",       # git → navigate
        "tikla": "click",        # tıkla → click
        "yaz": "type",           # yaz → type
        "kaydir": "scroll",      # kaydır → scroll
        "goruntu": "snapshot",   # görüntü → snapshot
        "gorsel": "vision",      # görsel → vision
        "durum": "status",       # durum → status
        "gezinti": "navigate",   # gezinti → navigate
        "ekran_al": "snapshot",  # ekran al → snapshot
        "js_calistir": "vision", # js çalıştır → vision (or add js_execute)
    }
    islem = _alias.get(islem, islem)
    # ... rest uses English command names
```

## Placement Rules

1. **Always after args validation, before the main if/elif chain** — so validation errors show the original input, not the mapped one
2. **Always use `.get(islem, islem)`** — so unknown commands pass through to the error handler naturally
3. **Keep the alias dict at function scope** — not module-level; it's only needed where the dispatch happens
4. **Document the alias direction** — a comment like `# Türkçe → İngilizce alias` tells the next developer which direction the mapping goes

## When to Use

- **Fork tools** where tests from upstream expect English but ReYMeN integrations expect Turkish
- **Any bilingual API** where the tool module must speak both languages
- **Migration phase** — during test consolidation, aliases let old Turkish tests pass while the API stabilizes on English

## When NOT to Use

- **If the tool module already has full Turkish support** — no aliases needed, just fix the tests
- **For internal-only functions** — aliases are for the public `run()` surface only
- **If the mapping creates ambiguity** — e.g. two Turkish words mapping to the same English command is fine, but the reverse would be a problem
