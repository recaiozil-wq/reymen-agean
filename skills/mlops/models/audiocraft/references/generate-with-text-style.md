---
skill_id: 876562911678
usage_count: 1
last_used: 2026-06-16
---
# Generate with text + style
descriptions = ["upbeat dance track"]
wav = model.generate_with_style(descriptions, style_audio, sr)
```

### Style-only generation (no text)

```python