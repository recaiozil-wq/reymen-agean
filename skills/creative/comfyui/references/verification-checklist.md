---
skill_id: 864eb247f2af
usage_count: 1
last_used: 2026-06-16
---
## Verification Checklist

Use `python3 scripts/health_check.py` to run the whole list at once. Manual:

- [ ] `hardware_check.py` verdict is `ok` OR the user explicitly chose Comfy Cloud
- [ ] `comfy --version` works (or `uvx --from comfy-cli comfy --help`)
- [ ] `curl http://HOST:PORT/system_stats` returns JSON
- [ ] `comfy model list` shows at least one checkpoint (local) OR
      `/api/experiment/models/checkpoints` returns models (cloud)
- [ ] Workflow JSON is in API format
- [ ] `check_deps.py` reports `is_ready: true` (or only `node_check_skipped`
      on cloud free tier)
- [ ] Test run with a small workflow completes; outputs land in `--output-dir`