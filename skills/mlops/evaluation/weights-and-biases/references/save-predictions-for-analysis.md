---
skill_id: 6ec1db06e706
usage_count: 1
last_used: 2026-06-16
---
# Save predictions for analysis
predictions_table = wandb.Table(
    columns=["id", "input", "prediction", "ground_truth"],
    data=predictions_data
)
wandb.log({"predictions": predictions_table})
```

### 5. Use Offline Mode for Unstable Connections

```python
import os