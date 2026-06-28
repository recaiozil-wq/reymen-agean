---
name: software-development-upstream-fork-comparison
description: Compare a local fork project against its upstream parent by reading both
  local docs and fetching upstream info from official sources.
title: Software Development Upstream Fork Comparison
version: 1.0.0
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | AI/ML mühendisi |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | AI/ML görevi gerektiğinde |
| **Neden?** | standardize etmek için |
| **Nasıl?** | Skill adımlarını takip ederek |

— read local project docs, fetch upstream official info, cross-reference features,
  produce comparison table
# Upstream vs Fork — Project Comparison

Compare a local fork project against its upstream parent by reading both local docs and fetching upstream info from official sources.

## Trigger

When the user asks about:
- "What's the difference between X and Y?"
- "Why is my fork different from the original?"
- Deeper investigation of how a local project relates to an upstream
- "Compare [local project] with [upstream project]"

## Workflow

### 1. Read Local Project Files

```yaml
priority: 
  - AGENTS.md (development guide, contribution rules, architecture)
  - README.md (project overview, features, setup)
  - CLAUDE.md / .cursorrules (if present)
```

Key things to extract:
- Project name and self-description
- Feature list
- How it describes its relationship to upstream (fork? built on? inspired by?)
- Any comparison tables already in the docs

### 2. Fetch Upstream Official Info

Use `web_extract` on the upstream's:
- Official website / landing page
- Docs site
- Releases / changelog page
- GitHub README

For Nous Research / Hermes Agent: `https://nousresearch.com/releases` has the full release catalog.

### 3. Cross-Reference & Compare

Build a comparison table with columns:

| Feature | Upstream | Fork |
|---------|:--------:|:----:|
| Developer | ... | ... |
| Release date | ... | ... |
| Core platform support | ... | ... |
| Unique additions (fork only) | ... | ... |
| Removed/changed features | ... | ... |

### 4. Deep Analysis — Code Health & Architecture

After the feature comparison, go deeper into code-level signals:

#### 4a. Try/Except Import Census
Scan the main entry point(s) for try/except import patterns:

```python
try:
    import gateway       # Silently fails on import error
except Exception:
    _GATEWAY = None
```

Count how many modules use this pattern vs direct imports. A high ratio (&gt;30%) indicates **modules that are written but not stable** — the system "works" because errors are silently swallowed. This is a critical fork-health metric.

How to check:
```
grep -c "try:" main.py
grep -c "^import " main.py
```

#### 4b. Protected Files Analysis
Check if the fork has a sync/update script with a protected files list. This reveals:
- Which files are truly custom (never overwritten by upstream)
- The fork's unique value proposition
- Maintainability risk (too many protected files = sync conflicts)

#### 4c. File Count & Module Categorization
Count total Python files and categorize them by size:

| Metric | What It Tells |
|--------|---------------|
| Total `.py` files | Codebase size |
| Root-level modules | Architecture complexity |
| Files over 500 lines | "God modules" — refactor candidates |
| Unused/imported ratio | Dead code indicator |

#### 4d. Architecture Dependency Diagram
Map how modules depend on each other to show coupling:

```
Upstream Core → Fork Entry (main.py) → Core modules (try/except)
                                     → Custom modules (direct import)
                                     → Specialized layer (standalone)
```

This reveals which parts of the fork are tightly coupled to upstream vs independently maintainable.

### 5. Answer the "Why First?" Question

Determine chronological order:
- **Upstream** is almost always older (the original)
- **Fork** branches off later
- Explain why the fork exists: additional features, different focus, platform specialization

## Pitfalls

- **Name collisions**: When the ReYMeN project is in the skills search path, many skill names collide with profile skills. Use absolute paths or unique names when possible.
- **Truncated output**: Large AGENTS.md files may be truncated when reading. Use `offset=` to read in chunks.
- **Web fetch may return summaries**: Large pages get LLM-summarized. For full data, use `web_extract` on specific subpages.
- **Local vs official naming**: The fork may rebrand itself (e.g., "ReYMeN Agent" vs "Hermes Agent"). The AGENTS.md / README.md will show the fork's self-identity.
- **Clean vs cluttered root**: Count root-level files and directories. A clean `src/` structure vs 300+ files in root indicates different maintenance philosophies — mention this in the comparison.
- **Dual comparison context**: When the fork project directory is also in the Hermes skills search path, skill names collide between profile and project. Load skills by their full profile path when ambiguity arises.

## Example Output Structure

```
## 🔍 Upstream vs Fork — Karşılaştırma

### Sıralama
| Sıra | Proje | Açıklama |
|:----:|-------|----------|
| 🥇 1. | **Upstream** (Orijinal) | ... |
| 🥈 2. | **Fork** (Özelleştirme) | ... |

### Feature Comparison Table
| Özellik | Upstream | Fork |
|---------|:--------:|:----:|
| ... | ... | ... |
```
