---
skill_id: 530bf39823b4
usage_count: 1
last_used: 2026-06-16
---
# Good: Save state_dict
torch.save(model.state_dict(), "model.pt")
```

__Remember__: PyTorch code should be device-agnostic, reproducible, and memory-conscious. When in doubt, profile with `torch.profiler` and check GPU memory with `torch.cuda.memory_summary()`.