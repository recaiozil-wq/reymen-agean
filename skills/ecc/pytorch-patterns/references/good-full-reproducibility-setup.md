---
skill_id: c1851e084a8b
usage_count: 1
last_used: 2026-06-16
---
# Good: Full reproducibility setup
def set_seed(seed: int = 42) -> None:
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False