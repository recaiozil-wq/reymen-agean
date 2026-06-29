---
name: native-mcp
title: "Native MCP"
tags: [mcp, protocol]
description: "MCP client: connect servers, register tools (stdio/HTTP)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [MCP, Tools, Integrations]
audience: user
related_skills: [mcporter]


---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | MCP entegratörü |
| **Ne?** | MCP client: connect servers, register tools (stdio/HTTP). |
| **Nerede?** | AI_ML/mcp/ |
| **Ne Zaman?** | ilgili görev gerektiğinde |
| **Neden?** | standardize etmek için |
| **Nasıl?** | Skill adımlarını takip ederek |


# Native Mcp

Bu skill modüler bir yönlendiricidir. İhtiyacınız olan bölümü seçin ve ilgili reference dosyasını yükleyin.

## 📂 Bölümler

| Bölüm | Reference Dosyası |
|-------|------------------|
| Native MCP Client | `references/native-mcp-client.md` |
| When to Use | `references/when-to-use.md` |
| Prerequisites | `references/prerequisites.md` |
| or, if using uv: | `references/or-if-using-uv.md` |
| Quick Start | `references/quick-start.md` |
| Configuration Reference | `references/configuration-reference.md` |
| How It Works | `references/how-it-works.md` |
| Transport Types | `references/transport-types.md` |
| Security | `references/security.md` |
| Only this token is passed to the subprocess | `references/only-this-token-is-passed-to-the-subprocess.md` |
| Troubleshooting | `references/troubleshooting.md` |
| Examples | `references/examples.md` |
| Sampling (Server-Initiated LLM Requests) | `references/sampling-server-initiated-llm-requests.md` |
| Notes | `references/notes.md` |

## Kullanım

1. İhtiyacın olan bölümü belirle
2. `skill_view(name="...", file_path="references/...")` ile yükle
