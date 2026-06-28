---
skill_id: 9a5b87e538ce
usage_count: 1
last_used: 2026-06-16
---
## Core Workflow

### 1. Define the Prediction Contract

Capture the product-level contract before writing model code:

- Prediction target and decision owner
- Input entity, output schema, confidence/calibration fields, and allowed latency
- Batch, online, streaming, or hybrid serving mode
- Fallback behavior when the model, feature store, or dependency is unavailable
- Human review or override path for high-impact decisions
- Privacy, retention, and audit requirements for inputs, predictions, and labels

Do not accept "improve the model" as a requirement. Tie the model to an observable product behavior and a measurable acceptance gate.

### 2. Lock the Data Contract

Every ML task needs an explicit data contract:

- Entity grain and primary key
- Label definition, label timestamp, and label availability delay
- Feature timestamp, freshness SLA, and point-in-time join rules
- Train, validation, test, and backtest split policy
- Required columns, allowed nulls, ranges, categories, and units
- PII or sensitive fields that must not enter training artifacts or logs
- Dataset version or snapshot ID for reproducibility

Guard against leakage first. If a feature is not available at prediction time, or is joined using future information, remove it or move it to an analysis-only path.

### 3. Build a Reproducible Pipeline

Training code should be runnable by another engineer without hidden notebook state:

- Use typed config files or dataclasses for all hyperparameters and paths
- Pin package and model dependencies
- Set random seeds and document any nondeterministic GPU behavior
- Record dataset version, code SHA, config hash, metrics, and artifact URI
- Save preprocessing logic with the model artifact, not separately in a notebook
- Keep train, eval, and inference transformations shared or generated from one source
- Make every step idempotent so retries do not corrupt artifacts or metrics

Prefer immutable values and pure transformation functions. Avoid mutating shared data frames or global config during feature generation.

```python
import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TrainingConfig:
    dataset_uri: str
    model_dir: Path
    seed: int
    learning_rate: float
    batch_size: int


def artifact_name(config: TrainingConfig, code_sha: str) -> str:
    config_key = f"{config.dataset_uri}:{config.seed}:{config.learning_rate}:{config.batch_size}"
    config_hash = hashlib.sha256(config_key.encode("utf-8")).hexdigest()[:12]
    return f"{code_sha[:12]}-{config_hash}"
```

### 4. Evaluate Before Promotion

Promotion criteria should be declared before training finishes:

- Baseline model and current production model comparison
- Primary metric aligned to product behavior
- Guardrail metrics for latency, calibration, fairness slices, cost, and error concentration
- Slice metrics for important cohorts, geographies, devices, languages, or data sources
- Confidence intervals or repeated-run variance when metrics are noisy
- Failure examples reviewed by a human for high-impact models
- Explicit "do not ship" thresholds

```python
PROMOTION_GATES = {
    "auc": ("min", 0.82),
    "calibration_error": ("max", 0.04),
    "p95_latency_ms": ("max", 80),
}


def assert_promotion_ready(metrics: dict[str, float]) -> None:
    missing = sorted(name for name in PROMOTION_GATES if name not in metrics)
    if missing:
        raise ValueError(f"Model promotion metrics missing required gates: {missing}")

    failures = {
        name: value
        for name, (direction, threshold) in PROMOTION_GATES.items()
        for value in [metrics[name]]
        if (direction == "min" and value < threshold)
        or (direction == "max" and value > threshold)
    }
    if failures:
        raise ValueError(f"Model failed promotion gates: {failures}")
```

Use offline metrics as gates, not guarantees. When the model changes product behavior, plan shadow evaluation, canary rollout, or A/B testing before full rollout.

### 5. Package for Serving

An ML artifact is production-ready only when the serving contract is testable:

- Model artifact includes version, training data reference, config, and preprocessing
- Input schema rejects invalid, stale, or out-of-range features
- Output schema includes model version and confidence or explanation fields when useful
- Serving path has timeout, batching, resource limits, and fallback behavior
- CPU/GPU requirements are explicit and tested
- Prediction logs avoid PII and include enough identifiers for debugging and label joins
- Integration tests cover missing features, stale features, bad types, empty batches, and fallback path

Never let training-only feature code diverge from serving feature code without a test that proves equivalence.

### 6. Operate the Model

Model monitoring needs both system and quality signals:

- Availability, error rate, timeout rate, queue depth, and p50/p95/p99 latency
- Feature null rate, range drift, categorical drift, and freshness drift
- Prediction distribution drift and confidence distribution drift
- Label arrival health and delayed quality metrics
- Business KPI guardrails and rollback triggers
- Per-version dashboards for canaries and rollbacks

Every deployment should have a rollback plan that names the previous artifact, config, data dependency, and traffic-switch mechanism.