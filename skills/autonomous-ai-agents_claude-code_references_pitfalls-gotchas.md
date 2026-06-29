---
name: autonomous-ai-agents_claude-code_references_pitfalls-gotchas
description: Pitfalls & Gotchas
title: "Autonomous Ai Agents Claude Code References Pitfalls Gotchas"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Pitfalls & Gotchas |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Pitfalls & Gotchas

1. **Interactive mode REQUIRES tmux** — Claude Code is a full TUI app. Using `pty=true` alone in Hermes terminal works but tmux gives you `capture-pane` for monitoring and `send-keys` for input, which is essential for orchestration.
2. **`--dangerously-skip-permissions` dialog defaults to "No, exit"** — you must send Down then Enter to accept. Print mode (`-p`) skips this entirely.
3. **`--max-budget-usd` minimum is ~$0.05** — system prompt cache creation alone costs this much. Setting lower will error immediately.
4. **`--max-turns` is print-mode only** — ignored in interactive sessions.
5. **Claude may use `python` instead of `python3`** — on systems without a `python` symlink, Claude's bash commands will fail on first try but it self-corrects.
6. **Session resumption requires same directory** — `--continue` finds the most recent session for the current working directory.
7. **`--json-schema` needs enough `--max-turns`** — Claude must read files before producing structured output, which takes multiple turns.
8. **Trust dialog only appears once per directory** — first-time only, then cached.
9. **Background tmux sessions persist** — always clean up with `tmux kill-session -t <name>` when done.
10. **Slash commands (like `/commit`) only work in interactive mode** — in `-p` mode, describe the task in natural language instead.
11. **`--bare` skips OAuth** — requires `ANTHROPIC_API_KEY` env var or an `apiKeyHelper` in settings.
12. **Context degradation is real** — AI output quality measurably degrades above 70% context window usage. Monitor with `/context` and proactively `/compact`.
13. **Windows `SetForegroundWindow` is unreliable** — On Windows, `SetForegroundWindow` has a documented race condition. When scripting VS Code focus, fall back to `Alt+Tab` via `WScript.Shell SendKeys` before calling `SetForegroundWindow`. Four-attempt sequence: (1) SetForegroundWindow, (2) Alt+Tab, (3) taskbar click via `postMessage`, (4) window text match loop.
14. **VS Code Claude Agent input location changes per session** — Do NOT store hardcoded coordinates for the Claude chat input box. Always use Command Palette route (`Ctrl+Shift+P` → "Claude: Focus on Chat Input") instead.
15. **Clipboard tildes/backticks break PowerShell `Set-Clipboard`** — Single quotes inside PowerShell command strings cause parse failures. For messages with special characters, use Python's `subprocess.run` with `win32clipboard` or write content to a temp file and pipe it.
