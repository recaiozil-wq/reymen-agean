---
skill_id: 445fba74b3a0
usage_count: 1
last_used: 2026-06-16
---
# Load model and processor
processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
model.to("cuda")