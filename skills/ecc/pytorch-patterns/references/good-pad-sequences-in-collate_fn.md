---
skill_id: 45d3b7a95eae
usage_count: 1
last_used: 2026-06-16
---
# Good: Pad sequences in collate_fn
def collate_fn(batch: list[tuple[torch.Tensor, int]]) -> tuple[torch.Tensor, torch.Tensor]:
    sequences, labels = zip(*batch)