---
skill_id: 35c5a014ed58
usage_count: 1
last_used: 2026-06-16
---
# Post-process masks to original size
masks = processor.image_processor.post_process_masks(
    outputs.pred_masks.cpu(),
    inputs["original_sizes"].cpu(),
    inputs["reshaped_input_sizes"].cpu()
)
```