---
name: mlops_models_segment-anything_references_use-smaller-model-for-limited-vram
description: Use smaller model for limited VRAM
title: "Mlops Models Segment Anything References Use Smaller Model For Limited Vram"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Use smaller model for limited VRAM |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Use smaller model for limited VRAM
sam = sam_model_registry["vit_b"](checkpoint="sam_vit_b_01ec64.pth")
