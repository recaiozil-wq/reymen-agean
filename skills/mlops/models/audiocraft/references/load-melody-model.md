---
skill_id: 0b0851972d2f
usage_count: 1
last_used: 2026-06-16
---
# Load melody model
model = MusicGen.get_pretrained('facebook/musicgen-melody')
model.set_generation_params(duration=30)