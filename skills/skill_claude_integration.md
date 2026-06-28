---
skill_id: 56a860186e6c
usage_count: 1
last_used: 2026-06-16
---
title: claude_integration
summary: Expose Claude Code integration and MCP server to ReYMeN and Obsidian
tags: [integration, claude, mcp]

description: |
  This skill documents how Claude Code can access ReYMeN' procedural skills
  and the Obsidian vault via workspace links and a minimal MCP-like server.

triggers:
  - trigger: "claude-integration"
    examples:
      - "Integrate Claude with ReYMeN knowledge base"

steps:
  - step: "Ensure workspace has junctions to ReYMeN skills and Obsidian vault"
    path: docs/hermes-skills, docs/obsidian-vault
  - step: "Place `.vscode/.instructions.md` and `.vscode/pre_prompt.md` in the workspace"
    path: .vscode/.instructions.md, .vscode/pre_prompt.md
  - step: "Run local MCP server to expose notes at http://127.0.0.1:7070"
    command: |
      python -m venv mcp_server/.venv
      .\mcp_server\.venv\Scripts\Activate.ps1
      pip install -r mcp_server/requirements.txt
      python mcp_server/app.py
  - step: "Use the server's `/search` and `/note` endpoints to fetch context"

notes: |
  Reference Obsidian note: Obsidian Vault/ReYMeN Memories/2026-06-11 Claude integration.md
  This skill was auto-generated from that note to make the integration discoverable by ReYMeN.
