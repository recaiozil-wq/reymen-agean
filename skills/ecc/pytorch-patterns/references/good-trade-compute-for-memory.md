---
skill_id: c3a0e6240b7e
usage_count: 1
last_used: 2026-06-16
---
# Good: Trade compute for memory
from torch.utils.checkpoint import checkpoint

class LargeModel(nn.Module):
    def forward(self, x: torch.Tensor) -> torch.Tensor: