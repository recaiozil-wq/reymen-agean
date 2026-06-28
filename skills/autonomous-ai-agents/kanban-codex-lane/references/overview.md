---
skill_id: bce059749d61
usage_count: 1
last_used: 2026-06-16
---
## Overview

This skill defines the lightweight ReYMeN+Codex dual-lane convention for Kanban workers. ReYMeN is always the task owner: it calls `kanban_show`, decides whether Codex is appropriate, creates or selects an isolated workspace, starts and monitors Codex, reconciles any diff, runs verification, and writes the final `kanban_complete` or `kanban_block` handoff. Codex is an input lane only. Codex output is not a task completion signal, not a trusted reviewer, and not allowed to write durable Kanban state directly.

The convention exists so a ReYMeN worker can use Codex for bounded implementation help without changing the dispatcher. The dispatcher must still spawn ReYMeN workers. A worker may optionally spawn Codex inside its own run, then accept, partially accept, or reject the lane after independent review and tests.