---
skill_id: 7c35bf7fc97e
usage_count: 1
last_used: 2026-06-16
---
## Python helper script (ergonomic alternative)

For faster one-liners that don't need hand-written GraphQL, this skill ships a stdlib Python CLI at `scripts/linear_api.py`. Zero dependencies. Same auth (reads `LINEAR_API_KEY`).

```bash
SCRIPT=$(dirname "$(find ~/.hermes -path '*skills/productivity/linear/scripts/linear_api.py' 2>/dev/null | head -1)")/linear_api.py

python3 "$SCRIPT" whoami
python3 "$SCRIPT" list-teams
python3 "$SCRIPT" get-issue ENG-42
python3 "$SCRIPT" get-document 38359beef67c      # fetch a doc by slugId from the URL
python3 "$SCRIPT" raw 'query { viewer { name } }'
```

All subcommands: `whoami`, `list-teams`, `list-projects`, `list-states`, `list-issues`, `get-issue`, `search-issues`, `create-issue`, `update-issue`, `update-status`, `add-comment`, `list-documents`, `get-document`, `search-documents`, `raw`. Run with `--help` for flags.

Use the script when: you want a quick answer without crafting GraphQL. Use curl when: you need a query the script doesn't wrap, or you want to compose filters inline.