---
name: ecc_redis-patterns_references_rate-limiting
description: Rate Limiting
title: "Ecc Redis Patterns References Rate Limiting"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Rate Limiting |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Rate Limiting

### Fixed Window (Simple)

```python
def is_rate_limited(user_id: int, limit: int = 100, window: int = 60) -> bool:
    key = f"ratelimit:{user_id}:{int(time.time()) // window}"
    pipe = r.pipeline(transaction=True)
    pipe.incr(key)
    pipe.expire(key, window)
    count, _ = pipe.execute()
    return count > limit
```

### Sliding Window (Lua — Atomic)

```lua
-- sliding_window.lua
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])

redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
local count = redis.call('ZCARD', key)

if count < limit then
    -- Use unique member (now + sequence) to avoid collisions within the same millisecond
    local seq_key = key .. ':seq'
    local seq = redis.call('INCR', seq_key)
    redis.call('EXPIRE', seq_key, math.ceil(window / 1000))
    redis.call('ZADD', key, now, now .. '-' .. seq)
    redis.call('EXPIRE', key, math.ceil(window / 1000))
    return 1
end
return 0
```

```python
sliding_window = r.register_script(open('sliding_window.lua').read())

def allow_request(user_id: int) -> bool:
    key = f"ratelimit:sliding:{user_id}"
    now = int(time.time() * 1000)
    return bool(sliding_window(keys=[key], args=[now, 60000, 100]))
```
