---
skill_id: bfebe34154a0
usage_count: 1
last_used: 2026-06-16
---
## Examples

**Add caching to a Django/Flask API endpoint:**
Use cache-aside with `setex` and a 5-minute TTL on the response. Key on the request parameters.

**Rate-limit an API by user:**
Use fixed-window with `pipeline(transaction=True)` for low-traffic endpoints; use sliding-window Lua for accurate per-user throttling.

**Coordinate a background job across workers:**
Use `acquire_lock` with a TTL that exceeds the expected job duration. Always release in a `finally` block.

**Fan-out notifications to multiple subscribers:**
Use Pub/Sub for fire-and-forget. Switch to Streams if you need guaranteed delivery or replay for late consumers.