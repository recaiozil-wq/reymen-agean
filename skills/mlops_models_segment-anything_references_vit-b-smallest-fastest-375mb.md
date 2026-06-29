---
name: mlops_models_segment-anything_references_vit-b-smallest-fastest-375mb
description: "ViT-B (smallest, fastest) - 375MB"
title: "Mlops Models Segment Anything References Vit B Smallest Fastest 375Mb"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | ViT-B (smallest, fastest) - 375MB |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# ViT-B (smallest, fastest) - 375MB
wget https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth
```

### Basic usage with SamPredictor

```python
import numpy as np
from segment_anything import sam_model_registry, SamPredictor
