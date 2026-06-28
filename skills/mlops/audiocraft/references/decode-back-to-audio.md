---
skill_id: 54c3202dbdb2
usage_count: 1
last_used: 2026-06-16
---
# Decode back to audio
with torch.no_grad():
    decoded = model.decode(codes)

torchaudio.save("reconstructed.wav", decoded[0].cpu(), sample_rate=32000)
```