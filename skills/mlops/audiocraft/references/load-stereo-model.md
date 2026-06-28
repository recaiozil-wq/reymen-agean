---
skill_id: eaaf2681c559
usage_count: 1
last_used: 2026-06-16
---
# Load stereo model
model = MusicGen.get_pretrained('facebook/musicgen-stereo-medium')
model.set_generation_params(duration=15)

descriptions = ["ambient electronic music with wide stereo panning"]
wav = model.generate(descriptions)