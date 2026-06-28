---
skill_id: fced66e9196f
usage_count: 1
last_used: 2026-06-16
---
# Loaded by ContextualMAB._load_seed() at engine init
{
  "skill-name": {"alpha": 1, "beta": 1, "total": 0, "category": "ecc"}
}
```

**Seed inheritance:** When a skill is first used in a new context (e.g. "kod"), `_ensure_arm()` checks the genel seed context first and inherits the seed alpha/beta values rather than starting fresh at 1/1. This prevents data fragmentation across contexts.

**Flat Thompson Sampling (v2.2 — 14 June 2026):** `_get_arm_data()` aggregates Beta data across ALL contexts when the specific context lacks data, preventing the context-fragmentation problem where 178 log entries are invisible because they were logged under a different context key. See `references/flat-thompson-sampling.md` for the algorithm.

**Shadow test (14 June 2026):** 23 queries across 10 categories showed MAB accuracy of 4.3% with 28 seeded skills and neutral priors. Root cause: insufficient pulls per arm (avg 6.3) and beta-skew from auto_reward false negatives. Recommendation: keep MAB in hybrid mode with threshold 0.70+ until 20+ pulls per commonly-used skill accumulate (~2-3 weeks at current usage rate). See `references/shadow-test-results.md` for full results.

**Maintenance:** Regenerate `skill_seed.json` whenever skills are added/removed. Keep the staged approach: add skills in category batches, not all at once. Run a shadow divergence check after each batch before expanding.

**Directory layout (current):**
```
rl_observation/
├── rl_skill_logger.py          ← Logger v1.5
├── rl_mab_engine.py            ← MAB v2.1 (Contextual + Seed)
├── rl_decision_layer.py        ← Hybrid karar katmani
├── rl_integration.py           ← CLI bridge
├── skill_log.jsonl             ← Append-only log
├── skill_seed.json             ← 44 skill seed (29 active + 15 windows-shortcuts pilot)
├── .gitignore                  ← log/cache/png hariç
├── monitor_log.py              ← İzleme
├── visualize_log.py            ← Görselleştirme
├── rl_stress_test.py           ← Cold-start test
└── TALIMAT_KILAVUZU.md         ← Doküman
```