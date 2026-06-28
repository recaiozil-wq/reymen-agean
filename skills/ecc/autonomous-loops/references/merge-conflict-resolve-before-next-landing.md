---
skill_id: f18ac6dad0e4
usage_count: 1
last_used: 2026-06-16
---
## MERGE CONFLICT — RESOLVE BEFORE NEXT LANDING

Your previous implementation conflicted with another unit that landed first.
Restructure your changes to avoid the conflicting files/lines below.

{full eviction context with diffs}
```

### Data Flow Between Stages

```
research.contextFilePath ──────────────────→ plan
plan.implementationSteps ──────────────────→ implement
implement.{filesCreated, whatWasDone} ─────→ test, reviews
test.failingSummary ───────────────────────→ reviews, implement (next pass)
reviews.{feedback, issues} ────────────────→ review-fix → implement (next pass)
final-review.reasoning ────────────────────→ implement (next pass)
evictionContext ───────────────────────────→ implement (after merge conflict)
```

### Worktree Isolation

Every unit runs in an isolated worktree (uses jj/Jujutsu, not git):
```
/tmp/workflow-wt-{unit-id}/
```

Pipeline stages for the same unit **share** a worktree, preserving state (context files, plan files, code changes) across research → plan → implement → test → review.

### Key Design Principles

1. **Deterministic execution** — Upfront decomposition locks in parallelism and ordering
2. **Human review at leverage points** — The work plan is the single highest-leverage intervention point
3. **Separate concerns** — Each stage in a separate context window with a separate agent
4. **Conflict recovery with context** — Full eviction context enables intelligent re-runs, not blind retries
5. **Tier-driven depth** — Trivial changes skip research/review; large changes get maximum scrutiny
6. **Resumable workflows** — Full state persisted to SQLite; resume from any point

### When to Use Ralphinho vs Simpler Patterns

| Signal | Use Ralphinho | Use Simpler Pattern |
|--------|--------------|-------------------|
| Multiple interdependent work units | Yes | No |
| Need parallel implementation | Yes | No |
| Merge conflicts likely | Yes | No (sequential is fine) |
| Single-file change | No | Yes (sequential pipeline) |
| Multi-day project | Yes | Maybe (continuous-claude) |
| Spec/RFC already written | Yes | Maybe |
| Quick iteration on one thing | No | Yes (NanoClaw or pipeline) |

---