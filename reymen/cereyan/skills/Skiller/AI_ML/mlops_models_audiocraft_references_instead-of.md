---
name: mlops_models_audiocraft_references_instead-of
description: Instead of
title: "Mlops Models Audiocraft References Instead Of"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Instead of |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Instead of
for desc in descriptions:
    wav = model.generate([desc])  # Multiple batches (slower)
```

### GPU memory requirements

| Model | FP32 VRAM | FP16 VRAM |
|-------|-----------|-----------|
| musicgen-small | ~4GB | ~2GB |
| musicgen-medium | ~8GB | ~4GB |
| musicgen-large | ~16GB | ~8GB |
