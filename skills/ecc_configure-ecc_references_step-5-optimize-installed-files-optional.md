---
name: ecc_configure-ecc_references_step-5-optimize-installed-files-optional
description: "Step 5: Optimize Installed Files (Optional)"
title: "Ecc Configure Ecc References Step 5 Optimize Installed Files Optional"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Step 5: Optimize Installed Files (Optional) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Step 5: Optimize Installed Files (Optional)

Use `AskUserQuestion`:

```
Question: "Would you like to optimize the installed files for your project?"
Options:
  - "Optimize skills" — "Remove irrelevant sections, adjust paths, tailor to your tech stack"
  - "Optimize rules" — "Adjust coverage targets, add project-specific patterns, customize tool configs"
  - "Optimize both" — "Full optimization of all installed files"
  - "Skip" — "Keep everything as-is"
```

### If optimizing skills:
1. Read each installed SKILL.md
2. Ask the user what their project's tech stack is (if not already known)
3. For each skill, suggest removals of irrelevant sections
4. Edit the SKILL.md files in-place at the installation target (NOT the source repo)
5. Fix any path issues found in Step 4

### If optimizing rules:
1. Read each installed rule .md file
2. Ask the user about their preferences:
   - Test coverage target (default 80%)
   - Preferred formatting tools
   - Git workflow conventions
   - Security requirements
3. Edit the rule files in-place at the installation target

**Critical**: Only modify files in the installation target (`$TARGET/`), NEVER modify files in the source ECC repository (`$ECC_ROOT/`).
