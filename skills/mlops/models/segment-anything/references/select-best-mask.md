---
skill_id: 60216aabd51f
usage_count: 1
last_used: 2026-06-16
---
# Select best mask
best_mask = masks[np.argmax(scores)]
```

### HuggingFace Transformers

```python
import torch
from PIL import Image
from transformers import SamModel, SamProcessor