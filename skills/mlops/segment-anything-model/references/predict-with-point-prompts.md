---
skill_id: eb50cd581461
usage_count: 1
last_used: 2026-06-16
---
# Predict with point prompts
input_point = np.array([[500, 375]])  # (x, y) coordinates
input_label = np.array([1])  # 1 = foreground, 0 = background

masks, scores, logits = predictor.predict(
    point_coords=input_point,
    point_labels=input_label,
    multimask_output=True  # Returns 3 mask options
)