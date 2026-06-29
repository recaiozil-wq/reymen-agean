---
name: rl-agent-optimization
description: Bu skill modüler bir yönlendiricidir. İhtiyacınız olan bölümü seçin ve
  ilgili reference dosyasını yükleyin.
title: Rl Agent Optimization
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

AI agent's decision-making — skill selection, model routing, and workflow choices.
  Covers Thompson Sampling, Epsilon-Greedy, reward engineering, shadow mode deployment,
  and cold-start mitigation.
# Rl Agent Optimization

Bu skill modüler bir yönlendiricidir. İhtiyacınız olan bölümü seçin ve ilgili reference dosyasını yükleyin.

## 📂 Bölümler

| Bölüm | Reference Dosyası |
|-------|------------------|
| Philosophy | `references/philosophy.md` |
| Core Architecture | `references/core-architecture.md` |
| Critical Workflow Order | `references/critical-workflow-order.md` |
| Implementation Status (v2.0 — 13 June 2026) | `references/implementation-status-v2-0-13-june-2026.md` |
| Each arm (skill) has a Beta(alpha, beta) distribution | `references/each-arm-skill-has-a-beta-alpha-beta-distribution.md` |
| Sample from each arm's distribution, pick highest | `references/sample-from-each-arm-s-distribution-pick-highest.md` |
| reward = 1 (success) or 0 (failure) | `references/reward-1-success-or-0-failure.md` |
| Final stable range: 0.60-0.75 depending on MAB confidence | `references/final-stable-range-0-60-0-75-depending-on-mab-confidence.md` |
| Clear match → use rule | `references/clear-match-use-rule.md` |
| Ambiguous → consult MAB | `references/ambiguous-consult-mab.md` |
| Log and return | `references/log-and-return.md` |
| Loaded by ContextualMAB._load_seed() at engine init | `references/loaded-by-contextualmab-_load_seed-at-engine-init.md` |
| Contextual Bandit (Advanced) | `references/contextual-bandit-advanced.md` |
| Risk Mitigation | `references/risk-mitigation.md` |
| Integration with Hermes Agent | `references/integration-with-hermes-agent.md` |
| Related Skills | `references/related-skills.md` |
| References | `references/references.md` |

## Kullanım

1. İhtiyacın olan bölümü belirle
2. `skill_view(name="...", file_path="references/...")` ile yükle
