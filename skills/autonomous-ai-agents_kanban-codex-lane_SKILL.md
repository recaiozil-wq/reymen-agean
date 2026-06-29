---
name: autonomous-ai-agents-kanban-codex-lane
description: Bu skill modüler bir yönlendiricidir. İhtiyacınız olan bölümü seçin ve
  ilgili reference dosyasını yükleyin.
title: Autonomous Ai Agents Kanban Codex Lane
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

implementation lane while Hermes keeps ownership of task lifecycle, reconciliation,
  testing, and handoff.
# Kanban Codex Lane

Bu skill modüler bir yönlendiricidir. İhtiyacınız olan bölümü seçin ve ilgili reference dosyasını yükleyin.

## 📂 Bölümler

| Bölüm | Reference Dosyası |
|-------|------------------|
| Overview | `references/overview.md` |
| When to Use | `references/when-to-use.md` |
| Ownership Rules | `references/ownership-rules.md` |
| Required Worktree and Branch Pattern | `references/required-worktree-and-branch-pattern.md` |
| Codex Capability Checks | `references/codex-capability-checks.md` |
| Mode Selection | `references/mode-selection.md` |
| Prompt Construction | `references/prompt-construction.md` |
| Monitoring, Timeout, and Kill Behavior | `references/monitoring-timeout-and-kill-behavior.md` |
| Reconciliation Checklist | `references/reconciliation-checklist.md` |
| kanban_complete Metadata Schema | `references/kanban_complete-metadata-schema.md` |
| Common Pitfalls | `references/common-pitfalls.md` |
| Verification Checklist | `references/verification-checklist.md` |

## Kullanım

1. İhtiyacın olan bölümü belirle
2. `skill_view(name="...", file_path="references/...")` ile yükle
