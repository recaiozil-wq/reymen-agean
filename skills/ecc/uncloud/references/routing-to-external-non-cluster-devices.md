---
skill_id: d74ada5eef14
usage_count: 1
last_used: 2026-06-16
---
## Routing to External (Non-Cluster) Devices

To expose an external device (e.g. BMC, NAS, router UI) via Caddy without running a real container:

**1. Create a Caddyfile snippet** (e.g. `~/device.caddyfile`):

```caddyfile
https://device.example.com {
    reverse_proxy https://192.168.1.x {
        transport http {
            tls_insecure_skip_verify   # needed for self-signed BMC certs
        }
    }
    log
}
```

For plaintext upstream: `reverse_proxy http://192.168.1.x:port`

**2. Register as a named service with no-op container:**

```bash
uc service run \
  --name device-bmc \
  --caddyfile ~/device.caddyfile \
  registry.k8s.io/pause:3.9
```

`pause` is a minimal no-op container — it does nothing, but gives Uncloud a service entry to attach the Caddyfile to.

**3. Verify:**

```bash
uc caddy config   # device.example.com block should appear
```

> `--caddyfile` cannot be combined with non-`@host` published ports.

**DNS tip:** A wildcard record (`*.yourdomain.com → cluster-public-ip`) means any new subdomain works immediately — no DNS change needed per service.

---