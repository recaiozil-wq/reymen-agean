---
skill_id: ae21c5b6962c
usage_count: 1
last_used: 2026-06-16
---
# Local (defaults to http://127.0.0.1:8188)
python3 scripts/run_workflow.py \
  --workflow workflow_api.json \
  --args '{"prompt": "a beautiful sunset over mountains", "seed": -1, "steps": 30}' \
  --output-dir ./outputs