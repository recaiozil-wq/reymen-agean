---
name: ecc_intent-driven-development_references_examples
description: Examples
title: "Ecc Intent Driven Development References Examples"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Examples |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Examples

**Quick Capture — "Add CSV export to the dashboard"**

```
Goal: Authenticated users can download dashboard data as a CSV file.
In scope: Export of currently filtered rows; filename includes date.
Out of scope: Scheduled exports, email delivery, Excel format.
Assumptions: Max row count is under 10k; no PII in exported fields.

AC-001: Export generates file with correct headers
- Scenario: authenticated user, at least one data row visible
- Action: click "Export CSV"
- Expected: browser downloads file with columns [id, name, created_at]
- Must not: expose internal fields or rows belonging to other users
- Verification: automated integration test + manual schema spot-check
- Priority: Required
```

**Full Acceptance Brief trigger — "Migrate user auth to OAuth"**

Auth change + external dependency + existing session data → Full Brief with Risk Review table,
blocking decisions on session invalidation strategy, and explicit rollback AC.

**Existing spec review — user pastes a PRD**

Skill reviews it for missing scope boundaries, unverifiable requirements ("the system shall be fast"),
and silent assumptions, then returns corrected or supplemental criteria without restarting discovery.
