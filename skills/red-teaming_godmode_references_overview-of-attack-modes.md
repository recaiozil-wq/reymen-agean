---
name: red-teaming_godmode_references_overview-of-attack-modes
description: Overview of Attack Modes
title: "Red Teaming Godmode References Overview Of Attack Modes"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Overview of Attack Modes |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Overview of Attack Modes

### 1. GODMODE CLASSIC — System Prompt Templates
Proven jailbreak system prompts paired with specific models. Each template uses a different bypass strategy:
- **END/START boundary inversion** (Claude) — exploits context boundary parsing
- **Unfiltered liberated response** (Grok) — divider-based refusal bypass
- **Refusal inversion** (Gemini) — semantically inverts refusal text
- **OG GODMODE l33t** (GPT-4) — classic format with refusal suppression
- **Zero-refusal fast** (Hermes) — uncensored model, no jailbreak needed

See `references/jailbreak-templates.md` for all templates.

### 2. PARSELTONGUE — Input Obfuscation (33 Techniques)
Obfuscates trigger words in the user's prompt to evade input-side safety classifiers. Three tiers:
- **Light (11 techniques):** Leetspeak, Unicode homoglyphs, spacing, zero-width joiners, semantic synonyms
- **Standard (22 techniques):** + Morse, Pig Latin, superscript, reversed, brackets, math fonts
- **Heavy (33 techniques):** + Multi-layer combos, Base64, hex encoding, acrostic, triple-layer

See `scripts/parseltongue.py` for the Python implementation.

### 3. ULTRAPLINIAN — Multi-Model Racing
Query N models in parallel via OpenRouter, score responses on quality/filteredness/speed, return the best unfiltered answer. Uses 55 models across 5 tiers (FAST/STANDARD/SMART/POWER/ULTRA).

See `scripts/godmode_race.py` for the implementation.
