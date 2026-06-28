---
name: mlops_models_audiocraft_references_encode-to-tokens
description: Encode to tokens
title: "Mlops Models Audiocraft References Encode To Tokens"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Encode to tokens |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Encode to tokens
with torch.no_grad():
    encoded = model.encode(wav.unsqueeze(0))
    codes = encoded[0]  # Audio codes
