---
skill_id: 43df541ffc42
usage_count: 1
last_used: 2026-06-16
---
# Run lm-eval
        os.system(f"lm_eval --model hf --model_args pretrained={checkpoint_path} ...")
```

**Step 4: Plot learning curves**

```python
import json
import matplotlib.pyplot as plt