---
skill_id: 6095bc4e627c
usage_count: 1
last_used: 2026-06-16
---
# Obsidian Sync Notes

## User requirement

- On every new ReYMeN launch, sync all installed skills into Obsidian.
- Keep a stable master index note in the vault.
- Do not rely on incremental terminal appends for sync notes.

## Vault master index

- Path: `<OBSIDIAN_VAULT_PATH>/ReYMeN Skills Sync.md`
- Update rule: overwrite full file with current `skills_list` output.
- Link style: plain markdown list; wikilinks only for GitHub references.

## Telegram monitor note

- Path: `<OBSIDIAN_VAULT_PATH>/Telegram Gateway Monitor.md`
- Update rule: append test result lines with timestamp.
- Cron job ID: `c854e9ceb1e6`
