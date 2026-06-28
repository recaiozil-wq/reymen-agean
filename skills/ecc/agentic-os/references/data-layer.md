---
skill_id: e599e1abb5ce
usage_count: 1
last_used: 2026-06-16
---
## Data Layer

The data layer is your filesystem. Use JSON for structured data and markdown for narrative content.

### JSON for Structured State

```json
// data/projects/website-v2.json
{
  "name": "Website v2",
  "status": "in-progress",
  "milestone": "beta-launch",
  "agents_involved": ["@dev", "@writer"],
  "files": {
    "spec": "docs/website-v2-spec.md",
    "design": "designs/website-v2.fig"
  },
  "metrics": {
    "commits": 47,
    "last_session": "2026-04-22T11:30:00Z"
  }
}
```

### Markdown for Narrative

Use markdown for anything a human reads: decisions, logs, research notes, contact records.

### Schema Evolution

Never rename existing fields. Add new fields and mark old ones deprecated:

```json
{
  "name": "Website v2",
  "status": "in-progress",
  "milestone": "beta-launch",
  "_deprecated_priority": "high",
  "priority_v2": { "level": "high", "rationale": "Blocks investor demo" }
}
```

This keeps historical data readable without migration scripts.