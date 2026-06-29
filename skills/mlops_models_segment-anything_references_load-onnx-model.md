---
name: mlops_models_segment-anything_references_load-onnx-model
description: Load ONNX model
title: "Mlops Models Segment Anything References Load Onnx Model"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Load ONNX model |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Load ONNX model
ort_session = onnxruntime.InferenceSession("sam_onnx.onnx")
