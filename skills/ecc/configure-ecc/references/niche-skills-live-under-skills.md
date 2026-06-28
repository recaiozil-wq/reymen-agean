---
skill_id: 8c56b2dc2cc9
usage_count: 1
last_used: 2026-06-16
---
# Niche skills live under skills/
cp -R "$ECC_ROOT/skills/<skill-name>" "$TARGET/skills/"
```

When iterating over globbed source directories, never pass a trailing-slash source directly to `cp`. Use the directory path as the destination name explicitly:

```bash
cp -R "${src%/}" "$TARGET/skills/$(basename "${src%/}")"
```

Note: `continuous-learning` and `continuous-learning-v2` have extra files (config.json, hooks, scripts) — ensure the entire directory is copied, not just SKILL.md.

---