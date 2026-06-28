---
skill_id: 4032c1f56d7f
usage_count: 1
last_used: 2026-06-16
---
# Bad: Everything in forward
class ImageClassifier(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, x):
        x = F.conv2d(x, weight=self.make_weight())  # Creates weight each call!
        return x
```

### Proper Weight Initialization

```python