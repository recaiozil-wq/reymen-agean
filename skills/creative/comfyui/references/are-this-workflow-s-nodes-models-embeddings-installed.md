---
skill_id: 91f48015eac9
usage_count: 1
last_used: 2026-06-16
---
# → are this workflow's nodes/models/embeddings installed?

python3 scripts/run_workflow.py \
  --workflow workflows/sd15_txt2img.json \
  --args '{"prompt": "test", "steps": 4}' \
  --output-dir ./test-outputs
```