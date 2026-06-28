---
name: ecc_perl-security_references_quick-security-checklist
description: Quick Security Checklist
title: "Ecc Perl Security References Quick Security Checklist"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Quick Security Checklist |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Quick Security Checklist

| Check | What to Verify |
|---|---|
| Taint mode | `-T` flag on CGI/web scripts |
| Input validation | Allowlist patterns, length limits |
| File operations | Three-arg open, path traversal checks |
| Process execution | List-form system, no shell interpolation |
| SQL queries | DBI placeholders, never interpolate |
| HTML output | `encode_entities()`, template auto-escape |
| CSRF tokens | Generated, verified on state-changing requests |
| Session config | Secure, HttpOnly, SameSite cookies |
| HTTP headers | CSP, X-Frame-Options, HSTS |
| Dependencies | Pinned versions, audited modules |
| Regex safety | No nested quantifiers, anchored patterns |
| Error messages | No stack traces or paths leaked to users |
