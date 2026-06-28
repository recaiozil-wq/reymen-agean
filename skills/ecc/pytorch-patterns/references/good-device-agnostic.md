---
skill_id: 207cddc20bf9
usage_count: 1
last_used: 2026-06-16
---
# Good: Device-agnostic
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = MyModel().to(device)
data = data.to(device)