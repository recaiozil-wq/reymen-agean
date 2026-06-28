---
skill_id: c30ec132f05e
usage_count: 1
last_used: 2026-06-16
---
# Ensure correct sample rate
if sr != 32000:
    resampler = torchaudio.transforms.Resample(sr, 32000)
    wav = resampler(wav)