---
name: software-development_reymen-hermes-sync_references_2026-06-30-merge-session
description: 2026-06-30 Merge Session Log
title: "Software Development Reymen Hermes Sync References 2026 06 30 Merge Session"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | 2026-06-30 Merge Session Log |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# 2026-06-30 Merge Session Log

## Context
Complete 3-step merge of Hermes → Reymen. Hermes was updated, Reymen needed to absorb changes while preserving customizations.

## Step 1 — Untouched Files (Copied Directly)
AGENTS.md (69KB), CONTRIBUTING.md (46KB), .env.example (24KB), .gitignore, .gitattributes, .hadolint.yaml, docs/ (8 files), assets/ (1 file), packaging/ (2 files)

## Step 2 — Missing Agent Modules (8 files)
Hermes `agent/` modules that Reymen root didn't have:
- coding_context.py (738L), credits_tracker.py (794L), errors.py (3L), runtime_cwd.py (62L)
- ssl_guard.py (94L), turn_context.py (146L root / 388L agent), turn_finalizer.py (428L), turn_retry_state.py (68L)

**Lesson:** 7/8 already existed in `agent/` directory — root copy was redundant but harmless.

## Step 3 — Shared File Merge

| File | Hermes | Reymen Old | Action |
|------|--------|-----------|--------|
| model_tools.py | 1,231L (tool defs) | 154L (benchmark) | Rename → benchmark_tools.py, copy Hermes |
| trajectory_compressor.py | 1,579L (training data) | 62L (runtime) | Rename → reymen_trajectory_compressor.py, copy Hermes |
| batch_runner.py | 1,321L (dataset batch) | 231L (parallel tasks) | Rename → reymen_batch_runner.py, copy Hermes |
| mcp_serve.py | 897L (message bridge) | 309L (agent expose) | Rename → reymen_mcp_serve.py, copy Hermes |
| toolsets.py | 912L | 882L | +read_terminal, +coding toolset |
| utils.py | 440L | 376L | +model_forces_max_completion_tokens() |
| run_agent.py | 5,461L | 4,831L | +_launch_cwd_for_session() |

## Duplicate Discovery (Root vs Agent/)
75 files exist in BOTH root/ and agent/ with different sizes. Root = Reymen simplified, agent/ = Hermes full. INTENTIONAL.

## GitHub Setup
- Repo: Watcher-Hermes/ReYMeN-Ajan (public)
- Self-update script: .hermes_sync.sh rewritten to pull from GitHub (not Hermes)
- Cron: `reymen-guncelleme` — every Monday 03:00
- Protected files: 13 Reymen-specific files

## User Preferences
- "Kalıcı olarak söylüyorum artık seçenek sorar isen Allow once seçerek ilerle onay bekleme" — reinforced approval rule
- "Hayir asla" — do ALL merges, don't skip based on your own analysis
- "Sakin githab yollama" — never push without explicit instruction
