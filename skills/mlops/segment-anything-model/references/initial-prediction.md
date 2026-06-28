---
skill_id: 1e94a260ff95
usage_count: 1
last_used: 2026-06-16
---
# Initial prediction
masks, scores, logits = predictor.predict(
    point_coords=np.array([[500, 375]]),
    point_labels=np.array([1]),
    multimask_output=True
)