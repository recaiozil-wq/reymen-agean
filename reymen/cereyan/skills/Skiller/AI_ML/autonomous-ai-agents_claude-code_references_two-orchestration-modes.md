---
name: autonomous-ai-agents_claude-code_references_two-orchestration-modes
description: Two Orchestration Modes
title: "Autonomous Ai Agents Claude Code References Two Orchestration Modes"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Two Orchestration Modes |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Two Orchestration Modes

Hermes interacts with Claude Code in two fundamentally different ways. Choose based on the task.

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
