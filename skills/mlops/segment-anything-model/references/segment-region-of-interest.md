---
skill_id: 3c7d3e9dbe30
usage_count: 1
last_used: 2026-06-16
---
# Segment region of interest
masks, scores, _ = predictor.predict(
    box=np.array([x1, y1, x2, y2]),  # ROI bounding box
    multimask_output=True
)
```