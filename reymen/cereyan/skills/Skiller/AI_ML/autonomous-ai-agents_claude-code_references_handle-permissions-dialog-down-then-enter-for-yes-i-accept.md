---
name: autonomous-ai-agents_claude-code_references_handle-permissions-dialog-down-then-enter-for-yes-i-accept
description: "Handle permissions dialog (Down then Enter for \"Yes, I accept\")"
title: "Autonomous Ai Agents Claude Code References Handle Permissions Dialog Down Then Enter For Yes I Accept"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Handle permissions dialog (Down then Enter for "Yes, I accept") |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Handle permissions dialog (Down then Enter for "Yes, I accept")
terminal(command="sleep 3 && tmux send-keys -t claude-work Down && sleep 0.3 && tmux send-keys -t claude-work Enter")
