---
skill_id: f18122ddebc4
usage_count: 1
last_used: 2026-06-16
---
# Producer
def emit(stream: str, event: dict):
    r.xadd(stream, event, maxlen=10000)  # Cap stream length