---
skill_id: 1856c3507f5a
usage_count: 1
last_used: 2026-06-16
---
# Batch / sweep: 8 random seeds, parallel up to cloud tier limit
python3 scripts/run_batch.py \
  --workflow sdxl.json \
  --args '{"prompt": "abstract"}' \
  --count 8 --randomize-seed --parallel 3 \
  --output-dir ./outputs/batch
```

`-1` for `seed` (or omitting it with `--randomize-seed`) generates a fresh
random seed per run.

### Step 4: Present results

The scripts emit JSON to stdout describing every output file:

```json
{
  "status": "success",
  "prompt_id": "abc-123",
  "outputs": [
    {"file": "./outputs/sdxl_00001_.png", "node_id": "9",
     "type": "image", "filename": "sdxl_00001_.png"}
  ]
}
```