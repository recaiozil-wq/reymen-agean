---
skill_id: 3ac87d64a056
usage_count: 1
last_used: 2026-06-16
---
# GitHub Search via Tor — Best Practices

## Why Tor for GitHub
- GitHub API rate limit: 60 req/hr (unauthenticated), 5000 req/hr (authenticated)
- Tor curl bypasses GitHub's IP-based rate limiting for read-only API calls
- Use `curl --socks5-hostname 127.0.0.1:9150` for ALL GitHub API queries

## Search Patterns

### Find ReYMeN-related repos
```
curl --socks5-hostname 127.0.0.1:9150 \
  "https://api.github.com/search/repositories?q=hermes+agent+KEYWORD&sort=stars&per_page=10"
```

### Find ReYMeN issues
```
curl --socks5-hostname 127.0.0.1:9150 \
  "https://api.github.com/search/issues?q=repo:NousResearch/hermes-agent+KEYWORD"
```

### Keywords to try
- `hermes+agent+skill` → skill repos
- `hermes+agent+mcp` → MCP servers
- `hermes+memory+agent` → memory systems
- `hermes+gui+OR+dashboard` → GUI projects
- `hermes+gateway+telegram` → messaging integrations
- `hermes+security+OR+injection` → security topics

## Navigation Flow (User Watching)

1. First, search API with curl → get list
2. Tell user what you found: "X reposu buldum, en iyisi Y"
3. Focus Tor: `focus_tor.ps1`
4. Navigate to best repo: `hermestor.py navigate "https://github.com/OWNER/REPO"`
5. Wait 4-5s
6. Screenshot + OCR to verify

## Repos Found (14 June 2026)

| Repo | Stars | Category |
|------|-------|----------|
| EKKOLearnAI/hermes-studio | 7.890 | Web dashboard (TypeScript) |
| awizemann/scarf | 623 | macOS/iOS app (Swift) |
| xaspx/hermes-control-interface | 762 | Web dashboard (JS) |
| JPeetz/ReYMeN-Studio | 195 | Multi-agent UI (TypeScript) |
| yoloshii/ClawMem | 182 | Memory layer |
| 410979729/scope-recall-hermes | 96 | Memory provider |
| mudrii/hermesd | 92 | TUI dashboard (Python) |
| Sibyl-Labs/Sibyl-Memory | 83 | Memory plugin |
| sanchomuzax/hermes-webui | 106 | Process monitoring |
| Noshkoto/hermes-share-skill | 0 | Session export skill |
| kingmt123/paper-deep-reader | 0 | Academic paper skill |
| shiro-0x/hersona | 0 | Personality templates |
| djairjr/hermes-agent-onboarding | 4 | Setup meta-skill |
