---
skill_id: aa9145d5caf7
usage_count: 1
last_used: 2026-06-16
---
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
