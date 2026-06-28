---
skill_id: 4358b5009c67
usage_count: 1
last_used: 2026-06-16
---
## Notes

- **Rate limits:** X enforces per-endpoint rate limits. A 429 means wait and retry. Write endpoints (post, reply, like, repost) have tighter limits than reads.
- **Scopes:** OAuth 2.0 tokens use broad scopes. A 403 on a specific action usually means the token is missing a scope — have the user re-run `xurl auth oauth2`.
- **Token refresh:** OAuth 2.0 tokens auto-refresh. Nothing to do.
- **Multiple apps:** Each app has isolated credentials/tokens. Switch with `xurl auth default` or `--app`.
- **Multiple accounts per app:** Select with `-u / --username`, or set a default with `xurl auth default APP USER`.
- **Token storage:** `~/.xurl` is YAML. In Docker, use the ReYMeN subprocess HOME (`/opt/data/home` in the official image) so tokens land under `/opt/data/home/.xurl`. Never read or send this file to LLM context.
- **Cost:** X API access is typically paid for meaningful usage. Many failures are plan/permission problems, not code problems.

---