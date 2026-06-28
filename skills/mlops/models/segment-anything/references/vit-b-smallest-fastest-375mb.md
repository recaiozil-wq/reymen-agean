---
skill_id: 41260eb03c9a
usage_count: 1
last_used: 2026-06-16
---
# ViT-B (smallest, fastest) - 375MB
wget https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth
```

### Basic usage with SamPredictor

```python
import numpy as np
from segment_anything import sam_model_registry, SamPredictor