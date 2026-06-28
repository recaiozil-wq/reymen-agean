---
name: mlops_models_segment-anything_references_reduce-points-for-automatic-generation
description: Reduce points for automatic generation
title: "Mlops Models Segment Anything References Reduce Points For Automatic Generation"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Reduce points for automatic generation |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Reduce points for automatic generation
mask_generator = SamAutomaticMaskGenerator(
    model=sam,
    points_per_side=16,  # Default is 32
)
