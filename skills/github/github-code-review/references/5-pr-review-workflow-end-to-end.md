---
skill_id: e61a4f0adcbe
usage_count: 1
last_used: 2026-06-16
---
## 5. PR Review Workflow (End-to-End)

When the user asks you to "review PR #N", "look at this PR", or gives you a PR URL, follow this recipe:

### Step 1: Set up environment

```bash
source "${REYMEN_HOME_PATH:-$HOME/.hermes}/skills/github/github-auth/scripts/gh-env.sh"