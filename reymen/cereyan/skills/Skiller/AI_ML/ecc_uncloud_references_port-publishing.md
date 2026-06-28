---
name: ecc_uncloud_references_port-publishing
description: Port Publishing
title: "Ecc Uncloud References Port Publishing"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Port Publishing |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

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
