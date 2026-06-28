---
name: autonomous-agent-harness
description: 'claude -p "Create a scheduled task: every weekday at 9am, review my
  GitHub notifications, open PRs, and calendar. Write a morning briefing to memory."'
title: Autonomous Agent Harness
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

## Active Tasks
- [ ] PR #123: Review and approve if CI green
- [ ] Monitor deploy: check /health every 30 min for 2 hours
- [ ] Research: Find 5 leads in AI tooling space
## Completed
- [x] Daily standup: reviewed 3 PRs, 2 issues
```
## Replacing Hermes
## Setup Guide
### Step 1: Configure MCP Servers
Ensure these are in `~/.claude.json`:
```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@anthropic/memory-mcp-server"]
    },
    "scheduled-tasks": {
      "command": "npx",
      "args": ["-y", "@anthropic/scheduled-tasks-mcp-server"]
    },
    "computer-use": {
      "command": "npx",
      "args": ["-y", "@anthropic/computer-use-mcp-server"]
    }
  }
}
```
### Step 2: Create Base Crons
```bash
# Daily morning briefing
claude -p "Create a scheduled task: every weekday at 9am, review my GitHub notifications, open PRs, and calendar. Write a morning briefing to memory."

# Continuous learning
claude -p "Create a scheduled task: every Sunday at 8pm, extract patterns from this week's sessions and update the learned skills."
```

### Step 3: Initialize Memory Graph

```bash
# Bootstrap your identity and context
claude -p "Create memory entities for: me (user profile), my projects, my key contacts. Add observations about current priorities."
```

### Step 4: Enable Computer Use (Optional)

Grant computer-use MCP the necessary permissions for browser and desktop control.

## Example Workflows

### Autonomous PR Reviewer
```
Cron: every 30 min during work hours
1. Check for new PRs on watched repos
2. For each new PR:
   - Pull branch locally
   - Run tests
   - Review changes with code-reviewer agent
   - Post review comments via GitHub MCP
3. Update memory with review status
```

### Personal Research Agent
```
Cron: daily at 6 AM
1. Check saved search queries in memory
2. Run Exa searches for each query
3. Summarize new findings
4. Compare against yesterday's results
5. Write digest to memory
6. Flag high-priority items for morning review
```

### Meeting Prep Agent
```
Trigger: 30 min before each calendar event
1. Read calendar event details
2. Search memory for context on attendees
3. Pull recent email/Slack threads with attendees
4. Prepare talking points and agenda suggestions
5. Write prep doc to memory
```

## Constraints

- Cron tasks run in isolated sessions — they don't share context with interactive sessions unless through memory.
- Computer use requires explicit permission grants. Don't assume access.
- Remote dispatch may have rate limits. Design crons with appropriate intervals.
- Memory files should be kept concise. Archive old data rather than letting files grow unbounded.
- Always verify that scheduled tasks completed successfully. Add error handling to cron prompts.
