---
skill_id: cb6290dcebb4
usage_count: 1
last_used: 2026-06-16
---
# 2026-05-21T06:18:05+0000 profile=writer prior_state=stopped action=registered
```

### Add a new static service

1. Create `docker/s6-rc.d/<name>/type` with `longrun\n` and `docker/s6-rc.d/<name>/run` (use `#!/command/with-contenv sh` + `# shellcheck shell=sh`).
2. Drop to hermes via `s6-setuidgid hermes` at the top of run (unless you specifically need root).
3. Create empty `docker/s6-rc.d/<name>/dependencies.d/base` so it waits for the base bundle.
4. Create empty `docker/s6-rc.d/user/contents.d/<name>` so it joins the user bundle.
5. The `COPY docker/s6-rc.d/` in the Dockerfile picks it up automatically — no other changes.

### Change the per-profile gateway run command

Edit `S6ServiceManager._render_run_script` in `hermes_cli/service_manager.py`. The function is also called by `hermes_cli/container_boot.py::_register_service` during boot reconciliation, so it's the single source of truth. Update the corresponding assertion in `tests/hermes_cli/test_service_manager.py::test_s6_register_creates_service_dir_and_triggers_scan`.

### Run the docker test harness

```sh
docker build -t hermes-agent-harness:latest .
HERMES_TEST_IMAGE=hermes-agent-harness:latest scripts/run_tests.sh tests/docker/ -v