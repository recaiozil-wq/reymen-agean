---
skill_id: 806834251d63
usage_count: 1
last_used: 2026-06-16
---
# Good: Call .item() only for logging
loss = criterion(output, target)
loss.backward()
print(f"Loss: {loss.item():.4f}")  # .item() after backward is fine