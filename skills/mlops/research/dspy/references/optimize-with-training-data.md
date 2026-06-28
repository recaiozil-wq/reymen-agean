---
skill_id: 443728676050
usage_count: 1
last_used: 2026-06-16
---
# Optimize with training data
from dspy.teleprompt import BootstrapFewShot

optimizer = BootstrapFewShot(metric=validate_answer)
optimized_rag = optimizer.compile(rag, trainset=trainset)
```