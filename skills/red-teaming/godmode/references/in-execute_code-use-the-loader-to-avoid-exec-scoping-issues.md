---
skill_id: bbc31811b853
usage_count: 1
last_used: 2026-06-16
---
# In execute_code — use the loader to avoid exec-scoping issues:
import os
exec(open(os.path.expanduser(
    os.path.join(os.environ.get("REYMEN_HOME_PATH", os.path.expanduser("~/.hermes")), "skills/red-teaming/godmode/scripts/load_godmode.py")
)).read())