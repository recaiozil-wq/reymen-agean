---
skill_id: c99dddb491dc
usage_count: 1
last_used: 2026-06-16
---
## Step 1: Automated Tests (mandatory, cannot skip)

Run these commands FIRST before any code review:

    npm run test       # Vitest test suite
    npm run build      # TypeScript type check + build

- If tests fail → report as highest priority bug
- If build fails → report type errors as highest priority
- Only proceed to Step 2 if both pass