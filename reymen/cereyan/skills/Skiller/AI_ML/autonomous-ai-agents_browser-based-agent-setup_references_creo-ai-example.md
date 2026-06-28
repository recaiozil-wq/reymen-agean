---
name: autonomous-ai-agents_browser-based-agent-setup_references_creo-ai-example
description: Creo AI Session Notes (2026-06-04)
title: "Autonomous Ai Agents Browser Based Agent Setup References Creo Ai Example"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Creo AI Session Notes (2026-06-04) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Creo AI Session Notes (2026-06-04)
- Platform: https://agent.creao.ai/chat
- Authenticated state required before configuring agents.
- Observed UI: login -> dashboard -> New Chat -> Connectors -> Schedule/Run Now.
- Intended autonomous flow:
  1. Add connectors: Outlook, X, YouTube, Google Sheets.
  2. Open New Chat, set model.
  3. Send setup prompt for morning-summary agent.
  4. Configure daily 08:00 Europe/Istanbul schedule.
  5. Test with Run Now.

### Browser Automation Lessons
- Playwright `launch_persistent_context` is required to reuse Chrome profile.
- Must close existing Chrome windows first or use `--profile-directory=Profile 1`.
- TargetClosedError on launch = profile-lock or other Chrome instance.
