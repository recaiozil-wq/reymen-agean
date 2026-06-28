---
skill_id: 461a30a770e1
usage_count: 1
last_used: 2026-06-16
---
## Port Publishing

### HTTP/HTTPS (via Caddy reverse proxy)

```
-p [hostname:]container_port[/protocol]
```

| Example | Meaning |
|---------|---------|
| `-p 8080/https` | HTTPS with auto `service-name.cluster-domain` hostname |
| `-p app.example.com:8080/https` | HTTPS with custom hostname |
| `-p 8080/http` | HTTP only, no TLS |

### TCP/UDP (host-bound, bypasses Caddy)

```
-p [host_ip:]host_port:container_port[/protocol]@host
```

| Example | Meaning |
|---------|---------|
| `-p 5432:5432@host` | TCP 5432 on all interfaces |
| `-p 127.0.0.1:5432:5432@host` | TCP 5432 loopback only |
| `-p 53:5353/udp@host` | UDP |

---