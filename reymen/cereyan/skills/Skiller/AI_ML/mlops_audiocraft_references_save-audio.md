---
name: mlops_audiocraft_references_save-audio
description: Save audio
title: "Mlops Audiocraft References Save Audio"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Save audio |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Save audio
torchaudio.save("output.wav", wav[0].cpu(), sample_rate=32000)
```

### Using HuggingFace Transformers

```python
from transformers import AutoProcessor, MusicgenForConditionalGeneration
import scipy
