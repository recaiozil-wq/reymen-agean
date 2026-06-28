---
skill_id: ac09549ca42b
usage_count: 1
last_used: 2026-06-16
---
# Reduce points for automatic generation
mask_generator = SamAutomaticMaskGenerator(
    model=sam,
    points_per_side=16,  # Default is 32
)