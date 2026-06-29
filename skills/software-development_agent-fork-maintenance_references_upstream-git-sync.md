---
name: software-development_agent-fork-maintenance_references_upstream-git-sync
description: Upstream Fork Git Sync Setup
title: "Software Development Agent Fork Maintenance References Upstream Git Sync"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Upstream Fork Git Sync Setup |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Upstream Fork Git Sync Setup

## Goal

Keep an `agent/` subdirectory synced with the upstream Hermes Agent while protecting ReYMeN-custom files in the root.

## Remote Setup

```bash
# Add upstream Hermes Agent repo
git remote add upstream https://github.com/nousresearch/hermes-agent.git

# Verify
git remote -v
# Should show:
#   origin    https://github.com/Watcher-Hermes/ReYMeN-Ajan.git (fetch/push)
#   upstream  https://github.com/nousresearch/hermes-agent.git (fetch/push)
```

## Manual Sync Procedure

```bash
# 1. Fetch upstream
git fetch upstream main

# 2. Check what changed in agent/
git diff --stat HEAD..upstream/main -- agent/

# 3. Update agent/ from upstream
git checkout upstream/main -- agent/

# 4. Protect ReYMeN files (restore local versions)
for f in main.py beyin.py motor.py cli.py guardrails.py \
         closed_learning_loop.py hata_cozucu.py tor_otomasyonu.py \
         araclar_nisan.py nisan_yakala.py otonom_nisan_olusturucu.py \
         akilli_yonlendirici.py cokus_raporlayici.py \
         provider_router.py planlayici.py robust_execution.py \
         insan_arayuzu.py vektorel_hafiza.py bounded_memory.py \
         adaptif_ogrenme.py reflexion_motoru.py anayasa_denetci.py \
         oz_yansima.py meta_prompt_optimizer.py oz_tutarlilik.py \
         beceri_kutuphanesi.py ajan_suru.py; do
    git checkout HEAD -- "$f" 2>/dev/null || true
done
```

## .hermes_sync.sh Script

The script handles four modes:
- No args: Show sync status (ahead/behind counts)
- `--sync`: Fetch upstream, update agent/, protect custom files
- `--diff`: Show agent/ changes since last sync
- `--reset`: Force-reset agent/ from upstream (asks for confirmation)

## Protected Files List

27 files that are ReYMeN-custom and should NEVER be overwritten by upstream:

**Core:** main.py, beyin.py, motor.py, cli.py, guardrails.py
**Learning:** closed_learning_loop.py, adaptif_ogrenme.py, reflexion_motoru.py
**Windows:** tor_otomasyonu.py, hata_cozucu.py, araclar_nisan.py, nisan_yakala.py, otonom_nisan_olusturucu.py
**Routing:** akilli_yonlendirici.py, provider_router.py, planlayici.py
**Safety:** cokus_raporlayici.py, robust_execution.py, insan_arayuzu.py
**Memory:** vektorel_hafiza.py, bounded_memory.py
**Self-improvement:** oz_yansima.py, meta_prompt_optimizer.py, oz_tutarlilik.py, beceri_kutuphanesi.py, ajan_suru.py
**Constitution:** anayasa_denetci.py

## Conflict Prevention

- The `git checkout upstream/main -- agent/` pattern ONLY touches the `agent/` directory
- Root files are never affected by the sync
- After sync, `git checkout HEAD -- protected_files` restores any that the sync might have touched (safety net)
- No `git merge` or `git rebase` needed — this is a file-level checkout, not a branch merge
