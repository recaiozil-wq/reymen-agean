---
skill_id: 864eb247f2af
usage_count: 1
last_used: 2026-06-16
---
## Verification Checklist

- [ ] After `pip install debugpy`, confirm: `python -c "import debugpy; print(debugpy.__version__)"`
- [ ] For remote debug, confirm the port is actually listening: `ss -tlnp | grep 5678`
- [ ] First breakpoint actually hits (if it doesn't, you likely have `PYTHONBREAKPOINT=0`, you're under xdist, or execution finished before attach)
- [ ] `where` / `w` shows the expected call stack
- [ ] Post-debug cleanup: no stray `breakpoint()` / `set_trace()` in committed code
  ```bash
  rg -n 'breakpoint\(\)|set_trace\(|debugpy\.listen' --type py
  ```