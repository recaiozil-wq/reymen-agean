---
skill_id: 0c7587fe870b
usage_count: 1
last_used: 2026-06-16
---
# Foreground point
        masks, scores, _ = predictor.predict(
            point_coords=np.array([[x, y]]),
            point_labels=np.array([1]),
            multimask_output=True
        )