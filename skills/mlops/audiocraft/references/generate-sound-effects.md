---
skill_id: d8e1748dd6bb
usage_count: 1
last_used: 2026-06-16
---
# Generate sound effects
descriptions = ["dog barking in a park with birds chirping"]
wav = model.generate(descriptions)

torchaudio.save("sound.wav", wav[0].cpu(), sample_rate=16000)
```