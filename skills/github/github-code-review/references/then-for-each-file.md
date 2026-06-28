---
skill_id: 35a7791f0c26
usage_count: 1
last_used: 2026-06-16
---
# Then for each file:
git diff main...HEAD -- path/to/file.py
```

For each changed file, use `read_file` to see full context around the changes — diffs alone can miss issues visible only with surrounding code.

### Step 5: Run automated checks locally (if applicable)

```bash