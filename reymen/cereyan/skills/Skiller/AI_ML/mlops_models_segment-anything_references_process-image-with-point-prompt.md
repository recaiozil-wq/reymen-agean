---
name: mlops_models_segment-anything_references_process-image-with-point-prompt
description: Process image with point prompt
title: "Mlops Models Segment Anything References Process Image With Point Prompt"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Process image with point prompt |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Process image with point prompt
image = Image.open("image.jpg")
input_points = [[[450, 600]]]  # Batch of points

inputs = processor(image, input_points=input_points, return_tensors="pt")
inputs = {k: v.to("cuda") for k, v in inputs.items()}
