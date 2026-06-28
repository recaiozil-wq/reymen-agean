---
skill_id: d7cfbcbf9e6a
usage_count: 1
last_used: 2026-06-16
---
# Bounding box [x1, y1, x2, y2]
input_box = np.array([425, 600, 700, 875])

masks, scores, logits = predictor.predict(
    box=input_box,
    multimask_output=False
)
```

### Combined prompts

```python