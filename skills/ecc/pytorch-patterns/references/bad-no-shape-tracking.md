---
skill_id: 0e690a1d2668
usage_count: 1
last_used: 2026-06-16
---
# Bad: No shape tracking
def forward(self, x):
    x = self.conv1(x)
    x = self.pool(x)
    x = x.view(x.size(0), -1)  # What size is this?
    return self.fc(x)           # Will this even work?
```