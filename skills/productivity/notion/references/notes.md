---
skill_id: 4358b5009c67
usage_count: 1
last_used: 2026-06-16
---
## Notes

- Page/database IDs are UUIDs (with or without dashes — both accepted).
- Rate limit: ~3 requests/second average. The CLI doesn't bypass this.
- The API cannot set database **view** filters — that's UI-only.
- Use `"is_inline": true` when creating data sources to embed them in a page.
- Always pass `-s` to curl to suppress progress bars (cleaner agent output).
- Pipe JSON through `jq` when reading: `... | jq '.results[0].properties'`.
- Notion also ships an MCP server now (`Notion MCP`, ~91% more token-efficient on DB ops than the previous version) — wire it via ReYMeN' MCP support if you want streaming Notion access from inside a session, but the paths above are enough for most one-shot tasks.