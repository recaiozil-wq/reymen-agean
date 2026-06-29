---
name: hookify-rules
description: Hookify Rules skill for AI/ML operations.
title: Hookify Rules
version: 1.0.0
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | AI/ML mühendisi |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | AI/ML görevi gerektiğinde |
| **Neden?** | standardize etmek için |
| **Nasıl?** | Skill adımlarını takip ederek |

- field: file_path
  - field: new_text
You're adding an API key to a .env file. Ensure this file is in .gitignore!
```
**Condition fields by event:**
- bash: `command`
- file: `file_path`, `new_text`, `old_text`, `content`
- prompt: `user_prompt`
**Operators:** `regex_match`, `contains`, `equals`, `not_contains`, `starts_with`, `ends_with`
All conditions must match for rule to trigger.
## Event Type Guide
### bash Events
Match Bash command patterns:
- Dangerous commands: `rm\s+-rf`, `dd\s+if=`, `mkfs`
- Privilege escalation: `sudo\s+`, `su\s+`
- Permission issues: `chmod\s+777`
### file Events
Match Edit/Write/MultiEdit operations:
- Debug code: `console\.log\(`, `debugger`
- Security risks: `eval\(`, `innerHTML\s*=`
- Sensitive files: `\.env$`, `credentials`, `\.pem$`
### stop Events
Completion checks and reminders. Pattern `.*` matches always.
### prompt Events
Match user prompt content for workflow enforcement.
## Pattern Writing Tips
### Regex Basics
- Escape special chars: `.` to `\.`, `(` to `\(`
- `\s` whitespace, `\d` digit, `\w` word char
- `+` one or more, `*` zero or more, `?` optional
- `|` OR operator
### Common Pitfalls
- **Too broad**: `log` matches "login", "dialog" — use `console\.log\(`
- **Too specific**: `rm -rf /tmp` — use `rm\s+-rf`
- **YAML escaping**: Use unquoted patterns; quoted strings need `\\s`
### Testing
```bash
python3 -c "import re; print(re.search(r'your_pattern', 'test text'))"
```
## File Organization
- **Location**: `.claude/` directory in project root
- **Naming**: `.claude/hookify.{descriptive-name}.local.md`
- **Gitignore**: Add `.claude/*.local.md` to `.gitignore`
## Commands
- `/hookify [description]` - Create new rules (auto-analyzes conversation if no args)
- `/hookify-list` - View all rules in table format
- `/hookify-configure` - Toggle rules on/off interactively
- `/hookify-help` - Full documentation
## Quick Reference
Minimum viable rule:
```markdown
Warning message here
```
