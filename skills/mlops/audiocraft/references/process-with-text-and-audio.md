---
skill_id: e7be99cc361d
usage_count: 1
last_used: 2026-06-16
---
# Process with text and audio
inputs = processor(
    audio=audio.squeeze().numpy(),
    sampling_rate=sr,
    text=["continue with a epic chorus"],
    padding=True,
    return_tensors="pt"
)