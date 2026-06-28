---
name: mlops_models_audiocraft_references_load-melody-model
description: Load melody model
title: "Mlops Models Audiocraft References Load Melody Model"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Load melody model |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Load melody model
model = MusicGen.get_pretrained('facebook/musicgen-melody')
model.set_generation_params(duration=30)
