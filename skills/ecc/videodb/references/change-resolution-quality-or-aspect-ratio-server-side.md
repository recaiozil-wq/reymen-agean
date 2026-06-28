---
skill_id: 1840e5b6f2c2
usage_count: 1
last_used: 2026-06-16
---
# Change resolution, quality, or aspect ratio server-side
job_id = conn.transcode(
    source="https://example.com/video.mp4",
    callback_url="https://example.com/webhook",
    mode=TranscodeMode.economy,
    video_config=VideoConfig(resolution=720, quality=23, aspect_ratio="16:9"),
    audio_config=AudioConfig(mute=False),
)
```

### Reframe aspect ratio (for social platforms)

**Warning:** `reframe()` is a slow server-side operation. For long videos it can take
several minutes and may time out. Best practices:
- Always limit to a short segment using `start`/`end` when possible
- For full-length videos, use `callback_url` for async processing
- Trim the video on a `Timeline` first, then reframe the shorter result

```python
from videodb import ReframeMode