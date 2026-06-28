---
name: mlops_models_audiocraft_references_load-audiogen
description: Load AudioGen
title: "Mlops Models Audiocraft References Load Audiogen"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Load AudioGen |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Load AudioGen
model = AudioGen.get_pretrained('facebook/audiogen-medium')

model.set_generation_params(duration=5)
