---
skill_id: 5e4878f2b3e6
usage_count: 1
last_used: 2026-06-16
---
## Quick Reference: PyTorch Idioms

| Idiom | Description |
|-------|-------------|
| `model.train()` / `model.eval()` | Always set mode before train/eval |
| `torch.no_grad()` | Disable gradients for inference |
| `optimizer.zero_grad(set_to_none=True)` | More efficient gradient clearing |
| `.to(device)` | Device-agnostic tensor/model placement |
| `torch.amp.autocast` | Mixed precision for 2x speed |
| `pin_memory=True` | Faster CPU→GPU data transfer |
| `torch.compile` | JIT compilation for speed (2.0+) |
| `weights_only=True` | Secure model loading |
| `torch.manual_seed` | Reproducible experiments |
| `gradient_checkpointing` | Trade compute for memory |