
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Hermes Backup Otomasyonu_References_Mnemosyne Migration |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Mnemosyne Migration Plan

> Researched: 2026-06-14
> Source: github.com/AxDSan/mnemosyne (v3.7.0, MIT)
> Hermes provider: `mnemosyne-hermes` pip package

## Overview

Mnemosyne is a zero-dependency, SQLite-backed AI memory system that replaces Hermes' built-in MEMORY.md/USER.md file system. It implements **BEAM** (Bilevel Episodic-Associative Memory) — a 3-tier architecture:

| Tier | Purpose | Details |
|------|---------|---------|
| Working Memory | Hot context, auto-injected before LLM calls | TTL-based eviction, max 10K items |
| Episodic Memory | Long-term storage | sqlite-vec + FTS5 hybrid search |
| TripleStore | Temporal knowledge graph | Version chains for facts |

**Key metrics:** 10M+ entries in single SQLite file, 65.2% BEAM benchmark (ICLR 2026), 98.9% LongMemEval.

## Prerequisites

- Hermes Agent installed (current version)
- Python 3.9+
- Disk space: ~50 MB (core) to ~1.5 GB (full with local embeddings + LLM)

## Migration Steps

### Step 1: Backup Current Memory

BEFORE installing Mnemosyne, snapshot current MEMORY.md and USER.md:

```bash
# Copy to Obsidian vault 08-Backup/ for permanent record
cp /c/Users/marko/AppData/Local/hermes/memories/MEMORY.md \
   "/c/Users/marko/OneDrive/Belgeler/Obsidian Vault/08-Backup/MEMORY-yedek-$(date +%Y-%m-%d).md"
cp /c/Users/marko/AppData/Local/hermes/memories/USER.md \
   "/c/Users/marko/OneDrive/Belgeler/Obsidian Vault/08-Backup/USER-yedek-$(date +%Y-%m-%d).md"
```

### Step 2: Install Mnemosyne

```bash
# Core only (uses Hermes' API for embeddings — ~50 MB RAM)
pip install mnemosyne-hermes

# Or with local embeddings (~800 MB RAM)
pip install "mnemosyne-hermes[embeddings]"

# Or full (~1.5 GB RAM)
pip install "mnemosyne-hermes[all]"
```

### Step 3: Link Plugin

Hermes discovers plugins by scanning `~/.hermes/plugins/`. Link the installed package:

```bash
mkdir -p ~/.hermes/plugins/mnemosyne
ln -sfn "$(python -c 'import pathlib, mnemosyne_hermes; print(pathlib.Path(mnemosyne_hermes.__file__).resolve().parent)')"/* ~/.hermes/plugins/mnemosyne/
```

### Step 4: Activate

```bash
hermes config set memory.provider mnemosyne
hermes memory setup
```

### Step 5: Migrate Existing Data

Write a script that reads MEMORY.md and USER.md content and calls `mnemosyne.remember()` for each fact. Example:

```python
from hermes_tools import read_file, terminal
from mnemosyne import remember

# Parse MEMORY.md sections (separated by § markers)
memory_content = read_file("/c/Users/marko/AppData/Local/hermes/memories/MEMORY.md")
entries = memory_content["content"].split("§")

for entry in entries:
    entry = entry.strip()
    if entry:
        remember(entry, importance=0.8, scope="global")

# Parse USER.md
user_content = read_file("/c/Users/marko/AppData/Local/hermes/memories/USER.md")
entries = user_content["content"].split("§")

for entry in entries:
    entry = entry.strip()
    if entry:
        remember(entry, importance=0.9, scope="global", source="user_preference")
```

### Step 6: Disable Built-in Memory

Edit `~/.hermes/config.yaml`:

```yaml
memory:
  memory_enabled: false
  user_profile_enabled: false
```

**WARNING:** Do NOT use `hermes tools disable memory` — that also kills all 23 Mnemosyne-registered tools.

### Step 7: Verify

```bash
hermes memory status       # Should show "Provider: mnemosyne"
hermes mnemosyne stats     # Working + episodic memory counts
```

## Architecture Details

```
┌──────────────────────────────────────────────────┐
│                 AI Agent                          │
└────────────────────┬─────────────────────────────┘
                     │ MCP / Plugin
┌────────────────────▼─────────────────────────────┐
│               Mnemosyne BEAM                       │
│  ┌──────────┐  ┌────────────┐  ┌──────────────┐  │
│  │ Working  │  │ Episodic   │  │ TripleStore   │  │
│  │ Memory   │─▶│ Memory     │  │ (Temporal KG) │  │
│  │ (hot)    │  │ (long-term)│  └──────────────┘  │
│  └──────────┘  └─────┬──────┘                     │
│                      │                              │
│           ┌──────────▼──────────┐                  │
│           │     SQLite DB       │                  │
│           │  sqlite-vec + FTS5  │                  │
│           └─────────────────────┘                  │
└────────────────────────────────────────────────────┘
```

**Hybrid scoring:** 50% vector similarity + 30% FTS5 rank + 20% importance, all inside SQLite.

**Binary vectors:** MIB (Mutual Information Binarization) compresses 384-dim float32 into 48 bytes — 32x reduction.

## Configuration Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MNEMOSYNE_DATA_DIR` | `~/.hermes/mnemosyne/data` | Database directory |
| `MNEMOSYNE_VEC_TYPE` | `int8` | Vector compression: float32, int8, or bit |
| `MNEMOSYNE_WM_MAX_ITEMS` | `10000` | Working memory limit |
| `MNEMOSYNE_RECENCY_HALFLIFE` | `168` | Decay in hours |
| `MNEMOSYNE_EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | Embedding model |

For Turkish support, swap to multilingual embeddings:
```bash
export MNEMOSYNE_EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

## 23 Registered Tools

| Category | Tools |
|----------|-------|
| Core memory (9) | remember, recall, sleep, stats, get, update, forget, invalidate, validate |
| Knowledge graph (4) | triple_add, triple_query, graph_query, graph_link |
| Multi-agent (4) | shared_remember, shared_recall, shared_forget, shared_stats |
| Working notes (3) | scratchpad_write, scratchpad_read, scratchpad_clear |
| Ops (3) | export, import, diagnose |

## Lifecycle Hooks

| Hook | Behavior |
|------|----------|
| `pre_llm_call` | Injects relevant working memory context into prompt |
| `on_session_start` | Initializes session-scoped memory state |
| `post_tool_call` | Captures tool results as memories (if configured) |

## Uninstall

```bash
pip uninstall mnemosyne-hermes
hermes config set memory.provider memory   # Switch back to built-in
hermes memory setup
```

## Pitfalls

1. **Don't use `hermes tools disable memory`** — kills all 23 Mnemosyne tools. Disable via config.yaml only.
2. **Embedding model change** — Changing model after data storage causes dimension mismatch. The vec0 virtual table is locked to the dimension it was created with.
3. **Data location** — Database lives at `~/.hermes/mnemosyne/data/mnemosyne.db` by default.
4. **LLM consolidation** — Mnemosyne uses a local MiniCPM5-1B GGUF for sleep/consolidation. Can route through Hermes' provider instead with `MNEMOSYNE_HOST_LLM_ENABLED=true`.
5. **Backup before migration** — MEMORY.md/USER.md content is NOT automatically imported. Must snapshot and migrate explicitly.
