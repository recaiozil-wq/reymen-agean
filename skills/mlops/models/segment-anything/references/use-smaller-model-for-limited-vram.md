---
skill_id: 9d5bfe4f7f33
usage_count: 1
last_used: 2026-06-16
---
# Use smaller model for limited VRAM
sam = sam_model_registry["vit_b"](checkpoint="sam_vit_b_01ec64.pth")