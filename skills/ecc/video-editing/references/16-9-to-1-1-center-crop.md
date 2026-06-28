---
skill_id: 5f52c5a00d6b
usage_count: 1
last_used: 2026-06-16
---
# 16:9 to 1:1 (center crop)
ffmpeg -i input.mp4 -vf "crop=ih:ih,scale=1080:1080" square.mp4
```

### Reframe with VideoDB

```python
from videodb import ReframeMode