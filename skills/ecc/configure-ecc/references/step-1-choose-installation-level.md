---
skill_id: 65d3e0c8166f
usage_count: 1
last_used: 2026-06-16
---
## Step 1: Choose Installation Level

Use `AskUserQuestion` to ask the user where to install:

```
Question: "Where should ECC components be installed?"
Options:
  - "User-level (~/.claude/)" — "Applies to all your Claude Code projects"
  - "Project-level (.claude/)" — "Applies only to the current project"
  - "Both" — "Common/shared items user-level, project-specific items project-level"
```

Store the choice as `INSTALL_LEVEL`. Set the target directory:
- User-level: `TARGET=~/.claude`
- Project-level: `TARGET=.claude` (relative to current project root)
- Both: `TARGET_USER=~/.claude`, `TARGET_PROJECT=.claude`

Create the target directories if they don't exist:
```bash
mkdir -p $TARGET/skills $TARGET/rules
```

---