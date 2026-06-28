---
skill_id: 0d8d7f088a57
usage_count: 1
last_used: 2026-06-16
---
# Ornekler:
run_cmd("ipconfig")
run_cmd("pip list", cwd=r"C:\Users\marko\hermes-ai")
run_cmd(r".\venv\Scripts\activate && python hermes.py --version",
        cwd=r"C:\Users\marko\hermes-ai")
```

### PowerShell komutu çalıştır

```python
import subprocess

def run_ps(script: str) -> str:
    result = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    return result.stdout + result.stderr