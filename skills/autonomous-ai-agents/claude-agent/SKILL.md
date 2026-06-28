---
name: claude-agent
title: "Claude Agent"
tags: [agents, ai]
description: Claude Code CLI agent modunu terminalde baslatma ve kullanma
version: 1.0.0
platforms: [windows]
metadata:
  hermes:
    tags: [claude, agent, terminal, cli, coding]
audience: user
related_skills: [powershell-claude-agent, codex, opencode]
---

# Claude Agent

Claude Code CLI (`claude`) agent modunda çalıştırma.

## Komut

```cmd
echo. | claude
```

- Not: `cmd /k` ile çalışır, PowerShell değil
- Windows'ta cmd.exe üzerinden çalıştırılmalı

## Kullanım

1. `cmd` (Command Prompt) aç
2. `echo. | claude` yaz → agent moduna geçer
3. Claude ile etkileşimli kodlama oturumu başlar

## Alternatif (PowerShell)

```powershell
echo "" | claude
```
