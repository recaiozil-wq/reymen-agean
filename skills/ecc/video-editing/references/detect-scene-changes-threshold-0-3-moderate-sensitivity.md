---
skill_id: ba42e12a10de
usage_count: 1
last_used: 2026-06-16
---
# Detect scene changes (threshold 0.3 = moderate sensitivity)
ffmpeg -i input.mp4 -vf "select='gt(scene,0.3)',showinfo" -vsync vfr -f null - 2>&1 | grep showinfo
```

### Silence detection for auto-cut

```bash