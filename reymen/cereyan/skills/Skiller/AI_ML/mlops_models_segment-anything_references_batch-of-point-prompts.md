---
name: mlops_models_segment-anything_references_batch-of-point-prompts
description: Batch of point prompts
title: "Mlops Models Segment Anything References Batch Of Point Prompts"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Batch of point prompts |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Batch of point prompts
points = [
    np.array([[100, 100]]),
    np.array([[200, 200]]),
    np.array([[300, 300]])
]

all_masks = []
for point in points:
    masks, scores, _ = predictor.predict(
        point_coords=point,
        point_labels=np.array([1]),
        multimask_output=True
    )
    all_masks.append(masks[np.argmax(scores)])
```
