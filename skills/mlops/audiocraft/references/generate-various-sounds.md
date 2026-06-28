---
skill_id: c79b07872bbc
usage_count: 1
last_used: 2026-06-16
---
# Generate various sounds
descriptions = [
    "thunderstorm with heavy rain and lightning",
    "busy city traffic with car horns",
    "ocean waves crashing on rocks",
    "crackling campfire in forest"
]

wav = model.generate(descriptions)

for i, audio in enumerate(wav):
    torchaudio.save(f"sound_{i}.wav", audio.cpu(), sample_rate=16000)
```