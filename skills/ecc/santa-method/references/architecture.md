---
skill_id: efe79c321127
usage_count: 1
last_used: 2026-06-16
---
## Architecture

```
┌─────────────┐
│  GENERATOR   │  Phase 1: Make a List
│  (Agent A)   │  Produce the deliverable
└──────┬───────┘
       │ output
       ▼
┌──────────────────────────────┐
│     DUAL INDEPENDENT REVIEW   │  Phase 2: Check It Twice
│                                │
│  ┌───────────┐ ┌───────────┐  │  Two agents, same rubric,
│  │ Reviewer B │ │ Reviewer C │  │  no shared context
│  └─────┬─────┘ └─────┬─────┘  │
│        │              │        │
└────────┼──────────────┼────────┘
         │              │
         ▼              ▼
┌──────────────────────────────┐
│        VERDICT GATE           │  Phase 3: Naughty or Nice
│                                │
│  B passes AND C passes → NICE  │  Both must pass.
│  Otherwise → NAUGHTY           │  No exceptions.
└──────┬──────────────┬─────────┘
       │              │
    NICE           NAUGHTY
       │              │
       ▼              ▼
   [ SHIP ]    ┌─────────────┐
               │  FIX CYCLE   │  Phase 4: Fix Until Nice
               │              │
               │ iteration++  │  Collect all flags.
               │ if i > MAX:  │  Fix all issues.
               │   escalate   │  Re-run both reviewers.
               │ else:        │  Loop until convergence.
               │   goto Ph.2  │
               └──────────────┘
```