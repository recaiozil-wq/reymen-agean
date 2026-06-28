---
skill_id: bfebe34154a0
usage_count: 1
last_used: 2026-06-16
---
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