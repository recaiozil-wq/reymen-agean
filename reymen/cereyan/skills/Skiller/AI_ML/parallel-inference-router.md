---
name: parallel-inference-router
description: Parallel Inference Router skill for AI/ML operations.
title: Parallel Inference Router
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

Hogwild!, and speculative decoding strategies.
Given a reasoning workload profile (token budget per task, task parallelism characteristics, model family, deployment target, latency budget), recommend a parallel-inference strategy or combination.
1. Task classification. Long reasoning (5k+ tokens), medium chain-of-thought (1k-5k), short chat (under 1k), or classification. Drives the first-pass decision.
2. Parallelism axis. Within-sequence (speculative decoding) vs across-sequence (voting, Hogwild!, multi-agent). Most workloads benefit from the within-sequence axis first.
3. Strategy recommendation. Pick from: speculative decoding only (safe default for any workload above 100 tokens), speculative + Hogwild! (long reasoning with parallelizable structure), tree-of-thought (explicit branch-and-prune problems), multi-agent (role-specialization problems), voting ensemble (high-stakes classification).
4. Parameter settings. For speculative decoding: draft family (EAGLE-3 default) and `N` (Phase 10 · 15 skill). For Hogwild!: worker count N (2 to 4, rarely more), coordination prompt template, single-node deployment confirmation.
5. Combined speedup estimate. If combining speculative decoding with Hogwild!, report the multiplicative speedup (typical range: 3x spec * 1.5-2x Hogwild! = 4.5-6x).
Hard rejects:
- Hogwild! for any workload under 2000 tokens. Coordination overhead dominates.
- Hogwild! on non-reasoning models (no emergent coordination).
- Multi-agent framework for problems that do not have a natural role decomposition.
- Tree-of-thought without explicit branch-and-prune logic (the strategy reduces to linear CoT otherwise).
- Running Hogwild! across nodes (cross-node cache synchronization is too slow).
Refusal rules:
- If the workload is experimental research, recommend Hogwild! as an experiment rather than a production bet. The speedups are task-dependent and real-world deployment is rare as of April 2026.
- If the user asks for guaranteed speedup, refuse and explain that only speculative decoding has the strong-guarantee property (output distribution preserved). Hogwild! is empirical.
- If the user has limited VRAM, refuse Hogwild! N>2 — each worker needs its own activation memory even though the cache is shared.
