---
skill_id: fcefa73a375e
usage_count: 1
last_used: 2026-06-16
---
# Load model
predictor = SamPredictor(sam)
predictor.set_image(image)

def on_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN: