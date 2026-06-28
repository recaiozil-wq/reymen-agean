---
skill_id: acb6a3e1d5d0
usage_count: 1
last_used: 2026-06-16
---
# force=True skips the error if the video is already indexed
video.index_spoken_words(force=True)
text = video.get_transcript_text()
stream_url = video.add_subtitle()
```

### Search inside videos

```python
from videodb.exceptions import InvalidRequestError

video.index_spoken_words(force=True)