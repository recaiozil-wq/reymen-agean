---
name: mlops_models_segment-anything_references_bounding-box-x1-y1-x2-y2
description: "Bounding box [x1, y1, x2, y2]"
title: "Mlops Models Segment Anything References Bounding Box X1 Y1 X2 Y2"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Bounding box [x1, y1, x2, y2] |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Bounding box [x1, y1, x2, y2]
input_box = np.array([425, 600, 700, 875])

masks, scores, logits = predictor.predict(
    box=input_box,
    multimask_output=False
)
```

### Combined prompts

```python
