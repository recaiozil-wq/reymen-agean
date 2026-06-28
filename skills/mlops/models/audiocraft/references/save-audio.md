---
skill_id: 7e6f2b509b85
usage_count: 1
last_used: 2026-06-16
---
# Save audio
torchaudio.save("output.wav", wav[0].cpu(), sample_rate=32000)
```

### Using HuggingFace Transformers

```python
from transformers import AutoProcessor, MusicgenForConditionalGeneration
import scipy