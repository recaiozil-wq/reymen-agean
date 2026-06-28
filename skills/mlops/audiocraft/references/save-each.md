---
skill_id: 95656c6aa4d6
usage_count: 1
last_used: 2026-06-16
---
# Save each
for i, audio in enumerate(wav):
    torchaudio.save(f"music_{i}.wav", audio.cpu(), sample_rate=32000)
```

### Melody-conditioned generation

```python
from audiocraft.models import MusicGen
import torchaudio