---
skill_id: 097a0e476415
usage_count: 1
last_used: 2026-06-16
---
## Evolution Across Model Capabilities

The harness should simplify as models improve. Following Anthropic's evolution:

### Stage 1 — Weaker Models (Sonnet-class)
- Full sprint decomposition required
- Context resets between sprints (avoid context anxiety)
- 2-agent minimum: Initializer + Coding Agent
- Heavy scaffolding compensates for model limitations

### Stage 2 — Capable Models (Opus 4.5-class)
- Full 3-agent harness: Planner + Generator + Evaluator
- Sprint contracts before each implementation phase
- 10-sprint decomposition for complex apps
- Context resets still useful but less critical

### Stage 3 — Frontier Models (Opus 4.6-class)
- Simplified harness: single planning pass, continuous generation
- Evaluation reduced to single end-pass (model is smarter)
- No sprint structure needed
- Automatic compaction handles context growth

> **Key principle:** Every harness component encodes an assumption about what the model can't do alone. When models improve, re-test those assumptions. Strip away what's no longer needed.