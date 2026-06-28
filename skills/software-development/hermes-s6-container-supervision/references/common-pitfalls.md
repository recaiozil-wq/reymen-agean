---
skill_id: 53cbf1a3890e
usage_count: 1
last_used: 2026-06-16
---
## Common pitfalls

### "command not found" via `docker exec`

`/command/` (where s6-overlay puts its binaries) is on PATH only for processes spawned by the supervision tree — services, cont-init.d, main-wrapper.sh. `docker exec <c> s6-svstat …` will fail with "command not found"; always use the absolute path `/command/s6-svstat`. The `hermes` binary works because the Dockerfile adds `/opt/hermes/.venv/bin` to the runtime `ENV PATH`.

### Profile directory ownership

The cont-init reconciler runs as hermes (`s6-setuidgid hermes` in `02-reconcile-profiles`). If a profile dir ends up root-owned (e.g. because `docker exec <c> hermes profile create …` ran as root by default), the reconciler can't read SOUL.md and fails with `PermissionError`. Mitigation: `stage2-hook.sh` chowns `$REYMEN_HOME_PATH/profiles` to hermes on **every** boot, idempotently. Don't remove that block.

### Files written by `docker exec` are root-owned

`docker exec` defaults to root. Either pass `--user hermes` or rely on the stage2 chown sweep next reboot. Don't write files under `$REYMEN_HOME_PATH/profiles/<name>/` as root manually — the next reconcile pass will sweep them but in-flight operations may hit perm errors.

### Service slot exists but s6-svstat says "s6-supervise not running"

The service directory is on tmpfs and was wiped on container restart. Either the cont-init reconciler hasn't run yet (give it a moment after `docker restart`) or it failed. Check `docker logs <c> | grep '02-reconcile'`.

### Gateway starts then immediately exits (`down (exitcode 1)` in svstat)

Most likely the profile has no model or auth configured. The service slot is correct — the gateway itself is unconfigured. Run `hermes -p <profile> setup` first. The s6 supervisor will keep restarting it; that's the desired behavior (when you fix the config, the next attempt succeeds and stays up).

### Reconciler skipped a profile

The reconciler keys on the **presence of `SOUL.md`** as the "real profile" marker. `hermes profile create` always seeds it. If a profile dir is missing SOUL.md (stray directory, partial restore, backup-in-progress), the reconciler skips it intentionally. Add a `SOUL.md` (even empty) to opt back in.

### "Help, the container exits 143!"

Check whether something is invoking `s6-svscanctl -t` or `/run/s6/basedir/bin/halt` — both cause /init to begin stage 3 shutdown but return 143 (SIGTERM) rather than the desired exit code. This was the Phase 2 architecture pivot from A to B. For container shutdown with a real exit code, you must let the CMD (main-wrapper.sh) exit normally; do **not** try to control exit from a finish script.