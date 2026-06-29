---
name: mlops_segment-anything-model_references_filter-by-predicted-iou
description: Filter by predicted IoU
title: "Mlops Segment Anything Model References Filter By Predicted Iou"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Filter by predicted IoU |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Filter by predicted IoU
high_quality = [m for m in masks if m['predicted_iou'] > 0.9]
