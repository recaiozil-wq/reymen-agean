---
skill_id: e78775f1a85a
usage_count: 1
last_used: 2026-06-16
---
## MusicGen usage

### Text-to-music generation

```python
from audiocraft.models import MusicGen
import torchaudio

model = MusicGen.get_pretrained('facebook/musicgen-medium')