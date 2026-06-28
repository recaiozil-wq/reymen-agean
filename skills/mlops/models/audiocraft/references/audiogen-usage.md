---
skill_id: 31e9fcddbd71
usage_count: 1
last_used: 2026-06-16
---
## AudioGen usage

### Sound effect generation

```python
from audiocraft.models import AudioGen
import torchaudio

model = AudioGen.get_pretrained('facebook/audiogen-medium')
model.set_generation_params(duration=10)