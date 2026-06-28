---
name: ecc_redis-patterns_references_consumer-group-guarantees-at-least-once-delivery
description: Consumer group — guarantees at-least-once delivery
title: "Ecc Redis Patterns References Consumer Group Guarantees At Least Once Delivery"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Consumer group — guarantees at-least-once delivery |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

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
