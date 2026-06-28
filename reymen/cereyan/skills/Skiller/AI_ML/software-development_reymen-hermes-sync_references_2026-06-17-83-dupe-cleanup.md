---
name: software-development_reymen-hermes-sync_references_2026-06-17-83-dupe-cleanup
description: 83 Duplicate File Cleanup — 17 Haziran 2026
title: "Software Development Reymen Hermes Sync References 2026 06 17 83 Dupe Cleanup"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | 83 Duplicate File Cleanup — 17 Haziran 2026 |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# 83 Duplicate File Cleanup — 17 Haziran 2026

## Context

Reymen (derived from Hermes Agent) had **83 files** duplicated between `root/` and `agent/` directories. Both copies of each file had different content — root had simplified Reymen versions, agent/ had full Hermes versions. This was intentional architecture but was NEVER documented, causing false "missing file" reports.

## Root Cause

When Reymen was forked from Hermes, the project maintained TWO parallel layers:
- **root/**: Reymen's simplified/stripped-down versions (used by beyin.py, motor.py, main.py)
- **agent/**: Hermes's full versions (used by run_agent.py, cli.py)

These were created during earlier merge sessions but never cleaned up or documented as intentional.

## Discovery

During Step 3 merge (2026-06-17), a root vs agent/ comparison revealed that **83 files** existed in both directories with different sizes. Only 3 import references from root duplicates were actually used (by `dispatcher.py`), confirming the rest were dormant.

## Cleanup Actions

### 1. Import Fix
- `dispatcher.py` line 15-16: `from tool_guardrails` → `from agent.tool_guardrails`
- `dispatcher.py` line 15-16: `from tool_executor` → `from agent.tool_executor`

### 2. Deletion
- Deleted 83 files from root/ that had agent/ equivalents
- Kept `reymen_batch_runner.py`, `reymen_mcp_serve.py`, `reymen_trajectory_compressor.py` (renamed originals)
- Kept `model_tools.py` (Hermes version, actually used by run_agent.py/cli.py)

### 3. Verification
- 9 critical files compiled: beyin.py, motor.py, main.py, closed_learning_loop.py, planlayici.py, dispatcher.py, sistem_talimati.py, cli.py, run_agent.py ✅

## Result
- **Before**: ~200 files in root (83 duplicates)
- **After**: 115 files in root (all Reymen-specific), 83 files in agent/ (all Hermes full versions)
- No functional change — both layers still work as intended

## Prevention

The `reymen-hermes-sync` skill now has:
1. A "CRITICAL RULE: Check ALL Layers Before Reporting" section
2. A "Cleanup Procedure" for duplicate discovery
3. Pitfall #7 about the root/agent layer confusion
