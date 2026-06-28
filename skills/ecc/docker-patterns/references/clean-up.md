---
skill_id: 9c9bd6c4b1ca
usage_count: 1
last_used: 2026-06-16
---
# Clean up
docker compose down                   # Stop and remove containers
docker compose down -v                # Also remove volumes (DESTRUCTIVE)
docker system prune                   # Remove unused images/containers
```

### Debugging Network Issues

```bash