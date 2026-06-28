---
skill_id: 4f9625493343
usage_count: 1
last_used: 2026-06-16
---
## How It Works

Uncloud runs Docker services across peer machines connected by a WireGuard mesh. Each machine is an equal cluster member; services communicate on the overlay network and Caddy runs globally to terminate public HTTP/HTTPS traffic. Compose files can use Uncloud extensions for ingress, placement, and generated Caddy configuration, while the `uc` CLI handles image distribution, scheduling, scaling, logs, and cluster state.