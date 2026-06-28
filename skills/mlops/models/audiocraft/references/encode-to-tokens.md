---
skill_id: acd109846547
usage_count: 1
last_used: 2026-06-16
---
# Encode to tokens
with torch.no_grad():
    encoded = model.encode(wav.unsqueeze(0))
    codes = encoded[0]  # Audio codes