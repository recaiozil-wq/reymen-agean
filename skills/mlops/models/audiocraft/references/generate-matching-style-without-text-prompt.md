---
skill_id: 3d10dab75193
usage_count: 1
last_used: 2026-06-16
---
# Generate matching style without text prompt
model.set_generation_params(
    duration=30,
    cfg_coef=3.0,
    cfg_coef_beta=None  # Disable double CFG for style-only
)

wav = model.generate_with_style([None], style_audio, sr)
```