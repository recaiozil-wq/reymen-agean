---
skill_id: 1edcc72df308
usage_count: 1
last_used: 2026-06-16
---
# List changed files
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/files \
  | python3 -c "
import sys, json
for f in json.load(sys.stdin):
    print(f\"{f['status']:10} +{f['additions']:-4} -{f['deletions']:-4}  {f['filename']}\")"
```

### Check Out PR Locally for Full Review

This works with plain `git` — no `gh` needed:

```bash