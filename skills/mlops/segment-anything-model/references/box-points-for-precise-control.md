---
skill_id: 20f8518a98ec
usage_count: 1
last_used: 2026-06-16
---
# Box + points for precise control
masks, scores, logits = predictor.predict(
    point_coords=np.array([[500, 375]]),
    point_labels=np.array([1]),
    box=np.array([400, 300, 700, 600]),
    multimask_output=False
)
```

### Iterative refinement

```python