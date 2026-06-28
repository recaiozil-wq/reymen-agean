---
skill_id: 44c41054368e
usage_count: 1
last_used: 2026-06-16
---
# Log tables
table = wandb.Table(columns=["id", "prediction", "ground_truth"])
wandb.log({"predictions": table})
```

### 4. Model Checkpointing

```python
import torch
import wandb