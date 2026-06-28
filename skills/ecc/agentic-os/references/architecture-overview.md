---
skill_id: f3d0538e7244
usage_count: 1
last_used: 2026-06-16
---
## Architecture Overview

The Agentic OS has four layers. Each layer is a directory in your project root.

```
project-root/
├── CLAUDE.md          # Kernel: identity, routing rules, agent registry
├── agents/            # Specialist agent definitions (markdown prompts)
├── .claude/commands/  # Slash commands: user-facing CLI
├── scripts/           # Daemon scripts: scheduled or event-driven tasks
└── data/              # State: JSON/markdown filesystem, no external DB
```

### Layer Responsibilities

| Layer | Purpose | Persistence |
|---|---|---|
| Kernel (`CLAUDE.md`) | Identity, routing, model policies, agent registry | Git-tracked |
| Agents (`agents/`) | Specialist identities with scoped tools and memory | Git-tracked |
| Commands (`.claude/commands/`) | User-facing slash commands (`/daily-sync`, `/outreach`) | Git-tracked |
| Scripts (`scripts/`) | Python/JS daemons triggered by cron or webhooks | Git-tracked |
| State (`data/`) | Append-only logs, project state, decision records | Git-ignored or tracked |