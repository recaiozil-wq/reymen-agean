---
name: runtime-shape
description: Runtime Shape skill for AI/ML operations.
title: Runtime Shape
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

event, cron, durable) and wire observability.
Given a task class (expected duration, step count, trigger type, latency budget), pick the runtime shape.
1. < 30s, user waits -> **request-response**.
2. Progressive UX or voice -> **streaming**.
3. Minutes to hours, user doesn't wait -> **queue-based**.
4. Reactive to external events -> **event-driven**.
5. Periodic housekeeping -> **cron**.
6. Any of the above where restart cost is high -> add **durable execution**.
1. The shape scaffold in your stack.
2. Observability: OTel GenAI spans (Lesson 23), backend wired (Lesson 24).
3. For queue: DLQ + retry policy + queue depth metric.
4. For event: explicit subscriber registry + replay path.
5. For cron: lock file or distributed lock to prevent overlapping runs.
6. For durable: checkpointer backend + resume semantics.
Hard rejects:
- Synchronous HTTP for a 5-minute task. Users hang up; workers pile up.
- Queue-based without DLQ. Failed jobs vanish.
- Background work without trace export. Failures invisible until users complain.
- "No durable state, we'll just retry." Long horizons must checkpoint.
Refusal rules:
- If the product has SLA + replay requirements, refuse swarm topology + non-durable runtime.
- If the task is compliance-bound, refuse event-driven without audit trail.
- If the user wants cron + no lock, refuse. Overlapping cron runs are duplicate work at best, data corruption at worst.
