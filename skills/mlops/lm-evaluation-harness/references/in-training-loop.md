---
skill_id: 9e5431fc3cf6
usage_count: 1
last_used: 2026-06-16
---
# In training loop
if step % eval_interval == 0:
    model.save_pretrained(f"checkpoints/step-{step}")