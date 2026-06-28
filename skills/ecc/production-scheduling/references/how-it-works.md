---
skill_id: 4f9625493343
usage_count: 1
last_used: 2026-06-16
---
## How It Works

1. Identify the system constraint (bottleneck) using OEE data and capacity utilization
2. Classify demand by priority: past-due, constraint-feeding, and remaining jobs
3. Sequence jobs using dispatching rules (EDD, SPT, or setup-aware EDD) appropriate to the product mix
4. Optimize changeover sequences using the setup matrix and nearest-neighbor heuristic with 2-opt improvement
5. Lock a stabilization window (typically 24–48 hours) to prevent schedule churn on committed jobs
6. Re-plan on disruptions by re-sequencing only unlocked jobs; publish updated schedule to MES