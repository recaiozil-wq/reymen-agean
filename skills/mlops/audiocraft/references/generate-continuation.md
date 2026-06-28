---
skill_id: 0303da7321e7
usage_count: 1
last_used: 2026-06-16
---
# Generate continuation
audio_values = model.generate(**inputs, do_sample=True, guidance_scale=3, max_new_tokens=512)
```