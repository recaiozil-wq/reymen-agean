---
name: ecc_agentic-os_references_daily-sync
description: /daily-sync
title: "Ecc Agentic Os References Daily Sync"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | /daily-sync |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# /daily-sync

Run the morning briefing:

1. Read `data/logs/last-sync.md` for context
2. Check project status: `git status`, pending PRs, CI health
3. Review `data/inbox/` for new tasks or decisions needed
4. Generate a summary of blockers, priorities, and next actions
5. Append the briefing to `data/logs/daily/<date>.md`
```

### Standard Command Set

| Command | Purpose |
|---|---|
| `/daily-sync` | Morning briefing: status, blockers, priorities |
| `/outreach` | Run outreach workflow (email, LinkedIn, etc.) |
| `/research <topic>` | Deep research with citation tracking |
| `/apply-jobs` | Tailor resume + cover letter for a target role |
| `/analytics` | Pull metrics from Stripe, GitHub, or custom sources |
| `/interview-prep` | Generate flashcards or mock interview questions |
| `/decision <topic>` | Log a decision with pros/cons and chosen path |

### Activating Commands

Place command files in `.claude/commands/<command-name>.md`. Claude Code auto-discovers them. Users invoke them with `/<command-name>`.
