---
skill_id: 1d71f6b47202
usage_count: 1
last_used: 2026-06-16
---
## Anti-Patterns

1. **Evaluator too lenient** — If the evaluator passes everything on iteration 1, your rubric is too generous. Tighten scoring criteria and add explicit penalties for common AI patterns.

2. **Generator ignoring feedback** — Ensure feedback is passed as a file, not inline. The generator should read `feedback-NNN.md` at the start of each iteration.

3. **Infinite loops** — Always set `GAN_MAX_ITERATIONS`. If the generator can't improve past a score plateau after 3 iterations, stop and flag for human review.

4. **Evaluator testing superficially** — The evaluator must use Playwright to **interact** with the live app, not just screenshot it. Click buttons, fill forms, test error states.

5. **Evaluator praising its own fixes** — Never let the evaluator suggest fixes and then evaluate those fixes. The evaluator only critiques; the generator fixes.

6. **Context exhaustion** — For long sessions, use Claude Agent SDK's automatic compaction or reset context between major phases.