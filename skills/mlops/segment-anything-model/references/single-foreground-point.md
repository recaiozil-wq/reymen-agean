---
skill_id: 5fafaa1a34df
usage_count: 1
last_used: 2026-06-16
---
# Single foreground point
input_point = np.array([[500, 375]])
input_label = np.array([1])

masks, scores, logits = predictor.predict(
    point_coords=input_point,
    point_labels=input_label,
    multimask_output=True
)