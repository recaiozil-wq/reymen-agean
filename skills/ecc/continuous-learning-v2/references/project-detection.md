---
skill_id: e6aaa2f4d7f7
usage_count: 1
last_used: 2026-06-16
---
## Project Detection

The system automatically detects your current project:

1. **`CLAUDE_PROJECT_DIR` env var** (highest priority)
2. **`git remote get-url origin`** -- hashed to create a portable project ID (same repo on different machines gets the same ID)
3. **`git rev-parse --show-toplevel`** -- fallback using repo path (machine-specific)
4. **Global fallback** -- if no project is detected, instincts go to global scope

Each project gets a 12-character hash ID (e.g., `a1b2c3d4e5f6`). A registry file at `${XDG_DATA_HOME:-~/.local/share}/ecc-homunculus/projects.json` maps IDs to human-readable names.

### Data Directory

Continuous-learning-v2 stores observer data outside `~/.claude` so Claude Code's sensitive-path guard does not block background instinct writes:

1. `CLV2_HOMUNCULUS_DIR` when set to an absolute path
2. `$XDG_DATA_HOME/ecc-homunculus`
3. `$HOME/.local/share/ecc-homunculus`

Existing users with data at `~/.claude/homunculus` can migrate once:

```bash
bash skills/continuous-learning-v2/scripts/migrate-homunculus.sh
```