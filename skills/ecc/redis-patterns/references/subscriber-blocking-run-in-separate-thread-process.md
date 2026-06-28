---
skill_id: 665b9b1eb811
usage_count: 1
last_used: 2026-06-16
---
# Subscriber (blocking — run in separate thread/process)
def subscribe_events(channel: str):
    pubsub = r.pubsub()
    pubsub.subscribe(channel)
    for message in pubsub.listen():
        if message['type'] == 'message':
            handle(json.loads(message['data']))
```

### Redis Streams (Durable Queue)

```python