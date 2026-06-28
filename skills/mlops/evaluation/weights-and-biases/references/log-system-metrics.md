---
skill_id: 91617440a166
usage_count: 1
last_used: 2026-06-16
---
# Log system metrics
wandb.log({
    "gpu/util": gpu_utilization,
    "gpu/memory": gpu_memory_used,
    "cpu/util": cpu_utilization
})