---
name: ecc_uncloud_references_common-mistakes
description: Common Mistakes
title: "Ecc Uncloud References Common Mistakes"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Common Mistakes |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Editing the Caddyfile directly | Use `x-caddy` in compose or `--caddyfile` on `uc service run` |
| Proxying an HTTPS upstream with self-signed cert | Add `transport http { tls_insecure_skip_verify }` |
| `uc caddy config` shows no user-defined blocks | Caddy admin socket unreachable — check `uc inspect caddy` and `uc logs caddy` |
| Service can't reach external LAN IP from container | Verify Caddy container's host can route to target network |
| Volumes lost after `uc service rm` | Named volumes persist; only anonymous volumes are auto-removed |
