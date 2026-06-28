---
skill_id: 8acd8ab70535
usage_count: 1
last_used: 2026-06-16
---
## Two Orchestration Modes

ReYMeN interacts with Claude Code in two fundamentally different ways. Choose based on the task.

### Mode 1: Print Mode (`-p`) — Non-Interactive (PREFERRED for most tasks)

Print mode runs a one-shot task, returns the result, and exits. No PTY needed. No interactive prompts. This is the cleanest integration path.

```
terminal(command="claude -p 'Add error handling to all API calls in src/' --allowedTools 'Read,Edit' --max-turns 10", workdir="/path/to/project", timeout=120)
```

**When to use print mode:**
- One-shot coding tasks (fix a bug, add a feature, refactor)
- CI/CD automation and scripting
- Structured data extraction with `--json-schema`
- Piped input processing (`cat file | claude -p "analyze this"`)
- Any task where you don't need multi-turn conversation

**Print mode skips ALL interactive dialogs** — no workspace trust prompt, no permission confirmations. This makes it ideal for automation.

### Mode 2: Interactive PTY via tmux — Multi-Turn Sessions

Interactive mode gives you a full conversational REPL where you can send follow-up prompts, use slash commands, and watch Claude work in real time. **Requires tmux orchestration.**

```