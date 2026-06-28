---
skill_id: d660cffdbaae
usage_count: 1
last_used: 2026-06-16
---
## Quick recipes

### Verify s6 is PID 1 in a running container

```sh
docker exec <c> sh -c 'cat /proc/1/comm; readlink /proc/1/exe'