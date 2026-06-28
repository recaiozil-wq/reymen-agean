---
skill_id: 88991505791c
usage_count: 1
last_used: 2026-06-16
---
## Step 4: Post-Installation Verification

After installation, perform these automated checks:

### 4a: Verify File Existence

List all installed files and confirm they exist at the target location:
```bash
ls -la $TARGET/skills/
ls -la $TARGET/rules/
```

### 4b: Check Path References

Scan all installed `.md` files for path references:
```bash
grep -rn "~/.claude/" $TARGET/skills/ $TARGET/rules/
grep -rn "../common/" $TARGET/rules/
grep -rn "skills/" $TARGET/skills/
```

**For project-level installs**, flag any references to `~/.claude/` paths:
- If a skill references `~/.claude/settings.json` — this is usually fine (settings are always user-level)
- If a skill references `~/.claude/skills/` or `~/.claude/rules/` — this may be broken if installed only at project level
- If a skill references another skill by name — check that the referenced skill was also installed

### 4c: Check Cross-References Between Skills

Some skills reference others. Verify these dependencies:
- `django-tdd` may reference `django-patterns`
- `laravel-tdd` may reference `laravel-patterns`
- `quarkus-tdd` may reference `quarkus-patterns`
- `springboot-tdd` may reference `springboot-patterns`
- `continuous-learning-v2` references `~/.claude/homunculus/` directory
- `python-testing` may reference `python-patterns`
- `golang-testing` may reference `golang-patterns`
- `crosspost` references `content-engine` and `x-api`
- `deep-research` references `exa-search` (complementary MCP tools)
- `fal-ai-media` references `videodb` (complementary media skill)
- `x-api` references `content-engine` and `crosspost`
- Language-specific rules reference `common/` counterparts

### 4d: Report Issues

For each issue found, report:
1. **File**: The file containing the problematic reference
2. **Line**: The line number
3. **Issue**: What's wrong (e.g., "references ~/.claude/skills/python-patterns but python-patterns was not installed")
4. **Suggested fix**: What to do (e.g., "install python-patterns skill" or "update path to .claude/skills/")

---