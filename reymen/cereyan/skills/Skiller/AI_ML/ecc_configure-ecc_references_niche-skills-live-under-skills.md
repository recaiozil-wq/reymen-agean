---
name: ecc_configure-ecc_references_niche-skills-live-under-skills
description: Niche skills live under skills/
title: "Ecc Configure Ecc References Niche Skills Live Under Skills"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Niche skills live under skills/ |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Niche skills live under skills/
cp -R "$ECC_ROOT/skills/<skill-name>" "$TARGET/skills/"
```

When iterating over globbed source directories, never pass a trailing-slash source directly to `cp`. Use the directory path as the destination name explicitly:

```bash
cp -R "${src%/}" "$TARGET/skills/$(basename "${src%/}")"
```

Note: `continuous-learning` and `continuous-learning-v2` have extra files (config.json, hooks, scripts) — ensure the entire directory is copied, not just SKILL.md.

---
