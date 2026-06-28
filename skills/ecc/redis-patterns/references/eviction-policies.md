---
skill_id: 5982b63abef2
usage_count: 1
last_used: 2026-06-16
---
## Eviction Policies

| Policy | Behavior | Best For |
|--------|----------|----------|
| `noeviction` | Error on write when full | Queues / critical data |
| `allkeys-lru` | Evict least recently used | General cache |
| `volatile-lru` | LRU only among keys with TTL | Mixed data store |
| `allkeys-lfu` | Evict least frequently used | Skewed access patterns |
| `volatile-ttl` | Evict soonest-to-expire | Prioritize long-lived data |

Set via `redis.conf`: `maxmemory-policy allkeys-lru`