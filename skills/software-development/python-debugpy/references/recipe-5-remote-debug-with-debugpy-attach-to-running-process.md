---
skill_id: 66ee8512d84a
usage_count: 1
last_used: 2026-06-16
---
## Recipe 5: Remote debug with debugpy (attach to running process)

For long-lived processes: ReYMeN gateway, tui_gateway, a daemon, a process that's already misbehaving and can't be restarted clean.

### Setup

```bash
source /home/bb/hermes-agent/.venv/bin/activate
pip install debugpy
```

### Pattern A: Source-edit — process waits for debugger at launch

Add near the top of the entry point (or inside the function you want to debug):

```python
import debugpy
debugpy.listen(("127.0.0.1", 5678))
print("debugpy listening on 5678, waiting for client...", flush=True)
debugpy.wait_for_client()
debugpy.breakpoint()       # optional: pause immediately once attached
```

Start the process; it blocks on `wait_for_client()`.

### Pattern B: No source edit — launch with `-m debugpy`

```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client your_script.py arg1
```

Equivalent for module entry:

```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client -m your.module
```

### Pattern C: Attach to an already-running process

Needs the PID and debugpy preinstalled in the target's environment:

```bash
python -m debugpy --listen 127.0.0.1:5678 --pid <pid>