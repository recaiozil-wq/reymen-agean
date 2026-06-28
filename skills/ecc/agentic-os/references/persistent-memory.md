---
skill_id: 40ff9422b1ee
usage_count: 1
last_used: 2026-06-16
---
## Persistent Memory

Memory is file-based. No vector DB, no Redis, no PostgreSQL. JSON and markdown files in `data/` are the database.

### Memory Directory Structure

```
data/
├── daily-logs/         # Append-only daily activity logs
├── projects/           # Per-project context files
├── decisions/          # Architectural and business decisions (ADR format)
├── inbox/              # New tasks or ideas awaiting triage
├── contacts/           # People, companies, relationship notes
└── templates/          # Reusable prompts and formats
```

### Daily Log Format

```markdown