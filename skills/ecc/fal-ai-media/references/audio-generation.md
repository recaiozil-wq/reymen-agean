---
skill_id: e0ce2a7a0b19
usage_count: 1
last_used: 2026-06-16
---
## Audio Generation

### CSM-1B (Conversational Speech)
Text-to-speech with natural, conversational quality.

```
generate(
  app_id: "fal-ai/csm-1b",
  input_data: {
    "text": "Hello, welcome to the demo. Let me show you how this works.",
    "speaker_id": 0
  }
)
```

### ThinkSound (Video-to-Audio)
Generate matching audio from video content.

```
generate(
  app_id: "fal-ai/thinksound",
  input_data: {
    "video_url": "<video_url>",
    "prompt": "ambient forest sounds with birds chirping"
  }
)
```

### ElevenLabs (via API, no MCP)
For professional voice synthesis, use ElevenLabs directly:

```python
import os
import requests

resp = requests.post(
    "https://api.elevenlabs.io/v1/text-to-speech/<voice_id>",
    headers={
        "xi-api-key": os.environ["ELEVENLABS_API_KEY"],
        "Content-Type": "application/json"
    },
    json={
        "text": "Your text here",
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
)
with open("output.mp3", "wb") as f:
    f.write(resp.content)
```

### VideoDB Generative Audio
If VideoDB is configured, use its generative audio:

```python