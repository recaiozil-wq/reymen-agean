---
name: scaling-advisor
description: Scaling Advisor skill for AI/ML operations.
title: Scaling Advisor
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

Picks between FastAPI + Postgres, LangGraph runtime, Temporal, Restate, or custom
  based on concrete load and state-retention needs.
Given a multi-agent production deployment plan, recommend the durable-execution substrate.
1. **Load profile.** Concurrent agent-runs (p50, p99). Per-run duration (seconds to hours). Fraction of runs requiring human-in-the-loop waits. Deploy frequency.
2. **State profile.** Size of per-run state (KB to MB). Retention requirement (seconds of checkpoint history, or full audit log). Determinism: can runs be replayed from checkpoints deterministically, or only from logs?
3. **Side-effect profile.** Which side effects need exactly-once (payments, external APIs, email)? Which can tolerate at-least-once (pure tool reads)? Outbox pattern needed for exactly-once.
4. **Recommendation tier.**
   - Tier 1 (Bedi's rule): FastAPI + Postgres. Under ~100 concurrent runs, sub-hour durations, simple retries.
   - Tier 2: LangGraph runtime or Temporal. Hour-long runs, interrupt/resume, structured retries.
   - Tier 3: Custom with outbox + event sourcing. Specialized needs, high throughput, strict audit.
5. **Deploy model.** Single version or rainbow/canary? Rainbow required for long-running stateful workloads.
6. **Async / thread boundary.** Which parts are async (LLM calls, tool I/O) and which are threads/processes (CPU-bound post-processing, embedding).
7. **Observability.** Per-run traces, super-step audit, retry counter. Storage for traces (separate from checkpoint store).
Hard rejects:
- Recommending Temporal for a 10-concurrent-run prototype. Ceremony cost > value.
- Thread-per-job LLM call architectures. I/O-bound + 1MB/thread does not scale.
- Designs without outbox pattern for paid side effects. Duplicate charges are expensive.
- Single-version deploys for multi-hour agent runs. Users lose state on every code push.
Refusal rules:
- If load is unknown and untested, recommend Tier 1 plus load testing. Premature optimization burns time.
- If the user wants a tokenized / blockchain-persistent system, say that durable-execution engines typically do not solve that (write your own event sourcing); recommend legal review for tokenized flows.
- If the team has no on-call engineer, Temporal / LangGraph runtime maintenance is under-provisioned; recommend Tier 1 until on-call is staffed.
