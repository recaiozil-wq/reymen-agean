---
name: orch-fix-defect
description: 'Actor · action · target: **orch · fix · defect**. Thin wrapper over
  the shared'
title: Orch Fix Defect
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

fix to green, review, and gated commit — by delegating each phase to the matching
  ECC agent. Use when existing behavior is broken or wrong.
  fix to green, review, and gated commit — by delegating each phase to the matching
  ECC agent. Use when existing behavior is broken or wrong.
- ai
- automation
- development
# orch-fix-defect

Actor · action · target: **orch · fix · defect**. Thin wrapper over the shared
engine in [`orch-pipeline`](../orch-pipeline/SKILL.md).

## When to Use

- Something is **broken**: wrong output, an error, a crash, a regression.
- Distinguish from siblings:
  - behavior is correct but you want it different → `orch-change-feature`.
  - the capability does not exist yet → `orch-add-feature`.

## Operation settings

- **Default size floor:** small (often trivial).
- **Phase mask:** 0 → (light 2 only if root cause is non-obvious or standard+) →
  4 → 5 → 6. Research (1) is usually skipped.
- **First move (phase 4):** reproduce the bug as a **new failing** test
  (regression test), then fix until it goes green. Proving the bug exists first
  is what separates a fix from a tweak.

## How It Works

1. Run the `orch-pipeline` engine with the settings above.
2. If the root cause is unclear, scope it with `code-explorer` before the red
   test; escalate build breaks to `build-error-resolver` / `/build-fix`.
3. Stop at **Gate 1** (only if a plan was produced) and **Gate 2** (pre-commit).
4. Add `security-reviewer` if the defect sits in a security-sensitive path.

## Example

```
orch-fix-defect: poller crashes on empty NWS response
→ write failing test reproducing the crash → fix to green
→ code-review → commit  [GATE 2: confirm]   (commit: fix:)
```
