---
skill_id: f7e6c1e35caf
usage_count: 1
last_used: 2026-06-16
---
# Use with Trainer
trainer = Trainer(
    logger=wandb_logger,
    max_epochs=10
)

trainer.fit(model, datamodule=dm)
```

### Keras/TensorFlow

```python
import wandb
from wandb.keras import WandbCallback