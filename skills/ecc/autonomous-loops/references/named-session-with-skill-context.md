---
skill_id: e8e9e87a2669
usage_count: 1
last_used: 2026-06-16
---
# Named session with skill context
CLAW_SESSION=my-project CLAW_SKILLS=tdd-workflow,security-review node scripts/claw.js
```

### How It Works

1. Loads conversation history from `~/.claude/claw/{session}.md`
2. Each user message is sent to `claude -p` with full history as context
3. Responses are appended to the session file (Markdown-as-database)
4. Sessions persist across restarts

### When NanoClaw vs Sequential Pipeline

| Use Case | NanoClaw | Sequential Pipeline |
|----------|----------|-------------------|
| Interactive exploration | Yes | No |
| Scripted automation | No | Yes |
| Session persistence | Built-in | Manual |
| Context accumulation | Grows per turn | Fresh each step |
| CI/CD integration | Poor | Excellent |

See the `/claw` command documentation for full details.

---