---
skill_id: 52aded165360
usage_count: 1
last_used: 2026-06-16
---
# Publisher
def publish_event(channel: str, payload: dict):
    r.publish(channel, json.dumps(payload))