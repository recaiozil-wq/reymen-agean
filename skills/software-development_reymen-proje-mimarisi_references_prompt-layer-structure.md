---
name: software-development_reymen-proje-mimarisi_references_prompt-layer-structure
description: Prompt Layer Structure (Hermes Agent vs ReYMeN)
title: "Software Development Reymen Proje Mimarisi References Prompt Layer Structure"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Prompt Layer Structure (Hermes Agent vs ReYMeN) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Prompt Layer Structure (Hermes Agent vs ReYMeN)

## Hermes Agent 10-Katmanli Sistem Prompt Yapisi

| Katman | Icerik | Kaynak |
|--------|--------|--------|
| 1 | Agent Identity | `~/.hermes/SOUL.md` — `load_soul_md()` ile yuklenir |
| 2 | Tool-aware behavior guidance | Built-in (agent/prompt_builder.py) |
| 3 | Honcho static block | Honcho plugin (aktifse) |
| 4 | Optional system message | Config veya API override |
| 5 | Frozen MEMORY snapshot | `~/.hermes/memories/MEMORY.md` |
| 6 | Frozen USER profile snapshot | `~/.hermes/memories/USER.md` |
| 7 | Skills index | `skills/` dizininden otomatik |
| 8 | Context files | `AGENTS.md`, `.cursorrules`, `CLAUDE.md` |
| 9 | Timestamp + Session ID | Runtime |
| 10 | Platform hint | CLI / Telegram / Discord farki |

### load_soul_md() (Hermes)
```python
def load_soul_md() -> Optional[str]:
    soul_path = get_hermes_home() / "SOUL.md"
    if not soul_path.exists():
        return None
    content = soul_path.read_text(encoding="utf-8").strip()
    content = _scan_context_content(content, "SOUL.md")  # Security scan
    content = _truncate_content(content, "SOUL.md")       # 20k char cap
    return content
```

### run_conversation() Tool Call Loop
```
for each tool_call in response.tool_calls:
    1. Resolve handler from tools/registry.py
    2. Fire pre_tool_call plugin hook
    3. Check if dangerous command (tools/approval.py)
       - If dangerous: invoke approval_callback, wait for user
    4. Execute handler with args + task_id
    5. Fire post_tool_call plugin hook
    6. Append {"role": "tool", "content": result} to history
```

### run_conversation() Ana Akis
```
1. Generate task_id (uuid)
2. Append user message to history
3. Build/cache system prompt
4. Preflight compression check (>50% context)
5. Build API messages (OpenAI / Anthropic / Codex format)
6. Ephemeral prompt layers (budget, context pressure)
7. Prompt caching markers (Anthropic only)
8. Interruptible API call
9. Parse response → tool_calls loop OR text response
```

## ReYMeN prompt_builder.py

ReYMeN'de iki prompt_builder var:
- `prompt_builder.py` (kok, 499 satir) — ReYMeN'in kendi prompt insa motoru
- `agent/prompt_builder.py` (1.507 satir) — Hermes'ten fork edilmis, `load_soul_md()` dahil

### load_soul_md() (ReYMeN, agent/prompt_builder.py)
```python
def load_soul_md() -> Optional[str]:
    soul_path = get_ReYMeN_home() / "SOUL.md"
    if not soul_path.exists():
        return None
    content = soul_path.read_text(encoding="utf-8").strip()
    content = _scan_context_content(content, "SOUL.md")
    content = _truncate_content(content, "SOUL.md")
    return content
```

Hermes'tekiyle neredeyse ayni, sadece `get_hermes_home()` yerine `get_ReYMeN_home()` kullanir.

## Eksik Katmanlar (ReYMeN'de yapilmasi gereken)

ReYMeN'in `conversation_loop.py` (162 satir) Hermes'in `run_conversation()` (~3.900 satir) seviyesinde degil.
Eksiksiz bir implementasyon icin: `lOOP_UPDATE_TASK.md`

Kritik eksikler:
- task_id uretimi
- Provider-agnostik API message builder (OpenAI/Anthropic/Codex format)
- Ephemeral prompt layers (butce uyarisi, context pressure)
- Prompt caching markers
- Interruptible API call
- Tool call loop (pre/post hook, approval, registry)
