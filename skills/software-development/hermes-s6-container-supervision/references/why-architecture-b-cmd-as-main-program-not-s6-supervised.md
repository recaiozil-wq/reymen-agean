---
skill_id: 9adffb754b32
usage_count: 1
last_used: 2026-06-16
---
## Why Architecture B (CMD as main program, not s6-supervised)

The original plan (v1–v3) called for main hermes to run as a supervised s6-rc service. Two real s6-overlay v3 mechanics blocked that:

1. **cont-init.d scripts receive no CMD args** — so the stage2 hook can't parse `docker run <image> chat -q "hi"` to set `HERMES_ARGS` for a service `run` script to consume.
2. **`/run/s6/basedir/bin/halt` does NOT propagate the exit code** written to `/run/s6-linux-init-container-results/exitcode`. Containers always exit 143 (SIGTERM) regardless. Confirmed by skarnet (s6 author) in [issue #477](https://github.com/just-containers/s6-overlay/issues/477): _"if you want a container shutdown, you need to either have your CMD exit, or, if you have no CMD, write the container exit code you want then call halt"_.

So we use the s6-overlay-native CMD pattern: `ENTRYPOINT ["/init", "/opt/hermes/docker/main-wrapper.sh"]`. /init prepends the wrapper to user args automatically — so `docker run <image> --version` becomes `/init main-wrapper.sh --version`, and `--version` doesn't get intercepted by /init's POSIX shell. The wrapper drops to hermes via `s6-setuidgid`, then exec's the chosen program. The program's exit code becomes the container exit code, exactly matching the pre-s6 tini contract.

Trade-off: main hermes is unsupervised under s6. That exactly matches its behavior under tini (the pre-s6 image). Dashboard supervision is the only **new** guarantee — and per-profile gateways under `/run/service/` get full supervision.