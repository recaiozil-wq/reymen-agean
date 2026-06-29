---
name: autonomous-ai-agents_kanban-codex-lane_references_reconciliation-checklist
description: Reconciliation Checklist
title: "Autonomous Ai Agents Kanban Codex Lane References Reconciliation Checklist"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Reconciliation Checklist |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Reconciliation Checklist

Hermes must perform this checklist before accepting any Codex lane result:

- [ ] `git -C <WORKTREE> status --short --branch` shows only expected files.
- [ ] `git -C <WORKTREE> diff --stat` and `git diff` were reviewed by Hermes.
- [ ] No secrets, credentials, generated caches, unrelated data, or local artifacts are included.
- [ ] PMB safety constraints were preserved: no live REST order entry, no market orders, no execution crossing, no fake passive fills/PnL, no risk-gate weakening, no secrets.
- [ ] Codex commits are small enough to cherry-pick or squash cleanly.
- [ ] Hermes ran the canonical tests itself, using `scripts/run_tests.sh` for Hermes Agent or the repo's documented wrapper for other repos.
- [ ] Any Codex-run tests are listed separately from Hermes-run tests.
- [ ] Accepted commits/diffs were applied to the Hermes-owned workspace/branch.
- [ ] Rejected or partial work has a concrete reason and artifact path if useful.

Acceptance outcomes:

- `accepted`: Codex diff/commits were reviewed, applied, and verified.
- `partial`: Some Codex work was accepted after edits or cherry-picks; rejected parts are documented.
- `rejected`: No Codex changes were accepted; reason is documented.
- `timed_out`: Codex exceeded the lane budget; useful artifacts may or may not exist.
