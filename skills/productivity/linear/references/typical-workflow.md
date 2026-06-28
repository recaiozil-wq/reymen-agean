---
skill_id: af7e280ed75f
usage_count: 1
last_used: 2026-06-16
---
## Typical Workflow

1. **Query teams** to get team IDs and keys
2. **Query workflow states** for target team to get state UUIDs
3. **List or search issues** to find what needs work
4. **Create issues** with team ID, title, description, priority
5. **Update status** by setting `stateId` to the target workflow state
6. **Add comments** to track progress
7. **Mark complete** by setting `stateId` to the team's "completed" type state