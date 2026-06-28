---
skill_id: e09245effc62
usage_count: 1
last_used: 2026-06-16
---
## Troubleshooting

### "Skills not being picked up by Claude Code"
- Verify the skill directory contains a `SKILL.md` file (not just loose .md files)
- For user-level: check `~/.claude/skills/<skill-name>/SKILL.md` exists
- For project-level: check `.claude/skills/<skill-name>/SKILL.md` exists

### "Rules not working"
- Rules are flat files, not in subdirectories: `$TARGET/rules/coding-style.md` (correct) vs `$TARGET/rules/common/coding-style.md` (incorrect for flat install)
- Restart Claude Code after installing rules

### "Path reference errors after project-level install"
- Some skills assume `~/.claude/` paths. Run Step 4 verification to find and fix these.
- For `continuous-learning-v2`, the `~/.claude/homunculus/` directory is always user-level — this is expected and not an error.