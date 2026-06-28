---
skill_id: 1faa8539bee9
usage_count: 1
last_used: 2026-06-16
---
# Determine which method to use throughout this workflow
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"