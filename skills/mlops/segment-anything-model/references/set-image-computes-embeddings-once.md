---
skill_id: e6b5e49cf97f
usage_count: 1
last_used: 2026-06-16
---
# Set image (computes embeddings once)
image = cv2.imread("image.jpg")
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
predictor.set_image(image)