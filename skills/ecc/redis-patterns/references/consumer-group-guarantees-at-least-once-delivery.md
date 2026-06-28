---
skill_id: 12078103763e
usage_count: 1
last_used: 2026-06-16
---
# Consumer group — guarantees at-least-once delivery
try:
    r.xgroup_create('events:orders', 'processor', id='0', mkstream=True)
except Exception:
    pass  # Group already exists

def consume(stream: str, group: str, consumer: str):
    while True:
        messages = r.xreadgroup(group, consumer, {stream: '>'}, count=10, block=2000)
        for _, entries in (messages or []):
            for msg_id, data in entries:
                process(data)
                r.xack(stream, group, msg_id)
```

> Prefer **Streams** over Pub/Sub when you need delivery guarantees, consumer groups, or replay.