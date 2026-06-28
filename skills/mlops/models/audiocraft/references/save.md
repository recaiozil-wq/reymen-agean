---
skill_id: 43781db5c40e
usage_count: 1
last_used: 2026-06-16
---
# Save
sampling_rate = model.config.audio_encoder.sampling_rate
scipy.io.wavfile.write("output.wav", rate=sampling_rate, data=audio_values[0, 0].cpu().numpy())
```

### Text-to-sound with AudioGen

```python
from audiocraft.models import AudioGen