---
skill_id: e18cdb1e1f29
usage_count: 1
last_used: 2026-06-16
---
# Display best mask
        display_mask(masks[np.argmax(scores)])
```

### Workflow 2: Object extraction

```python
def extract_object(image, point):
    """Extract object at point with transparent background."""
    predictor.set_image(image)

    masks, scores, _ = predictor.predict(
        point_coords=np.array([point]),
        point_labels=np.array([1]),
        multimask_output=True
    )

    best_mask = masks[np.argmax(scores)]