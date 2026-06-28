---
skill_id: b0be89d863f2
usage_count: 1
last_used: 2026-06-16
---
# Load AudioGen
model = AudioGen.get_pretrained('facebook/audiogen-medium')

model.set_generation_params(duration=5)