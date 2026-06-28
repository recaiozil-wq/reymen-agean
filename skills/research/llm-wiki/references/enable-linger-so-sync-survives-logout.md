---
skill_id: 0ed1749995f6
usage_count: 1
last_used: 2026-06-16
---
# Enable linger so sync survives logout:
sudo loginctl enable-linger $USER
```

This lets the agent write to `~/wiki` on a server while you browse the same
vault in Obsidian on your laptop/phone — changes appear within seconds.