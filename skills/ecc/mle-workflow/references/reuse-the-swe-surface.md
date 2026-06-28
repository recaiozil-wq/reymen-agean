---
skill_id: 695e30368d89
usage_count: 1
last_used: 2026-06-16
---
## Reuse the SWE Surface

Do not treat MLE as separate from software engineering. Most ECC SWE workflows apply directly to ML systems, often with stricter failure modes:

The recommended `minimal --with capability:machine-learning` install keeps the core agent surface available alongside this skill. For skill-only or agent-limited harnesses, pair `skill:mle-workflow` with `agent:mle-reviewer` where the target supports agents.

| SWE surface | MLE use |
|-------------|---------|
| `product-capability` / `architecture-decision-records` | Turn model work into explicit product contracts and record irreversible data, model, and rollout choices |
| `repo-scan` / `codebase-onboarding` / `code-tour` | Find existing training, feature, serving, eval, and monitoring paths before introducing a parallel ML stack |
| `plan` / `feature-dev` | Scope model changes as product capabilities with data, eval, serving, and rollback phases |
| `tdd-workflow` / `python-testing` | Test feature transforms, split logic, metric calculations, artifact loading, and inference schemas before implementation |
| `code-reviewer` / `mle-reviewer` | Review code quality plus ML-specific leakage, reproducibility, promotion, and monitoring risks |
| `build-fix` / `pr-test-analyzer` | Diagnose broken CI, flaky evals, missing fixtures, and environment-specific model or dependency failures |
| `quality-gate` / `test-coverage` | Require automated evidence for transforms, metrics, inference contracts, promotion gates, and rollback behavior |
| `eval-harness` / `verification-loop` | Turn offline metrics, slice checks, latency budgets, and rollback drills into repeatable gates |
| `ai-regression-testing` | Preserve every production bug as a regression: missing feature, stale label, bad artifact, schema drift, or serving mismatch |
| `api-design` / `backend-patterns` | Design prediction APIs, batch jobs, idempotent retraining endpoints, and response envelopes |
| `database-migrations` / `postgres-patterns` / `clickhouse-io` | Version labels, feature snapshots, prediction logs, experiment metrics, and drift analytics |
| `deployment-patterns` / `docker-patterns` | Package reproducible training and serving images with health checks, resource limits, and rollback |
| `canary-watch` / `dashboard-builder` | Make rollout health visible with model-version, slice, drift, latency, cost, and delayed-label dashboards |
| `security-review` / `security-scan` | Check model artifacts, notebooks, prompts, datasets, and logs for secrets, PII, unsafe deserialization, and supply-chain risk |
| `e2e-testing` / `browser-qa` / `accessibility` | Test critical product flows that consume predictions, including explainability and fallback UI states |
| `benchmark` / `performance-optimizer` | Measure throughput, p95 latency, memory, GPU utilization, and cost per prediction or retrain |
| `cost-aware-llm-pipeline` / `token-budget-advisor` | Route LLM/embedding workloads by quality, latency, and budget instead of defaulting to the largest model |
| `documentation-lookup` / `search-first` | Verify current library behavior for model serving, feature stores, vector DBs, and eval tooling before coding |
| `git-workflow` / `github-ops` / `opensource-pipeline` | Package MLE changes for review with crisp scope, generated artifacts excluded, and reproducible test evidence |
| `strategic-compact` / `dmux-workflows` | Split long ML work into parallel tracks: data contract, eval harness, serving path, monitoring, and docs |