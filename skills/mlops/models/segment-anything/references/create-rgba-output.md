---
skill_id: 2c75e3758b8e
usage_count: 1
last_used: 2026-06-16
---
# Create RGBA output
    rgba = np.zeros((image.shape[0], image.shape[1], 4), dtype=np.uint8)
    rgba[:, :, :3] = image
    rgba[:, :, 3] = best_mask * 255

    return rgba
```

### Workflow 3: Medical image segmentation

```python