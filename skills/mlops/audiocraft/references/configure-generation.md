---
skill_id: 5c8fa7c7f26e
usage_count: 1
last_used: 2026-06-16
---
# Configure generation
model.set_generation_params(
    duration=30,          # Up to 30 seconds
    top_k=250,            # Sampling diversity
    top_p=0.0,            # 0 = use top_k only
    temperature=1.0,      # Creativity (higher = more varied)
    cfg_coef=3.0          # Text adherence (higher = stricter)
)