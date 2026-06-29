---
name: communication_session-aware-qa_references_example-repetition-session
description: "Session-Specific Example: Repetition Detection Trigger"
title: "Communication Session Aware Qa References Example Repetition Session"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Session-Specific Example: Repetition Detection Trigger |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Session-Specific Example: Repetition Detection Trigger

## Session Context

User asked the same question **3 times** in one conversation:

1. "Hangi modelsin" → answered "DeepSeek-Chat" ❌ (inconsistent)
2. "Hangi modelsin" → answered "DeepSeek V4 Flash" ✅
3. After other messages, asked again → should have detected repetition

User also asked "Kaç skill var" twice, where the answer changed from 60 to 1024 due to library growth.

## User's Explicit Instruction (Turkish)

> "Her sorumu gecmiste de sormuş olsam kontrol et"

Translation: "Check if I've asked this question in the past as well."

## What Went Wrong

1. **Inconsistent identity**: First answer was "DeepSeek-Chat" (incorrect model name), second was "DeepSeek V4 Flash" (correct). The user had to say "kendini değiştir" (change yourself) — meaning "you ARE that model, update your answer."
2. **No repetition detection**: After the user asked "Hangi modelsin" a 3rd time, I should have noted "bunu daha önce sormuştun" and given the consistent answer.
3. **Verification needed**: When user said "Tekrar kontrol et" for skill count, they wanted a fresh check rather than cached data.

## Correct Behavior

- Before answering any question → search current conv + past sessions for repeats
- For identity → always use one canonical name
- For dynamic data → verify fresh, explain changes
