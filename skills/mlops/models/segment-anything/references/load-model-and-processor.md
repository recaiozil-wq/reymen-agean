---
skill_id: 445fba74b3a0
usage_count: 1
last_used: 2026-06-16
---
# Load model and processor
model = SamModel.from_pretrained("facebook/sam-vit-huge")
processor = SamProcessor.from_pretrained("facebook/sam-vit-huge")
model.to("cuda")