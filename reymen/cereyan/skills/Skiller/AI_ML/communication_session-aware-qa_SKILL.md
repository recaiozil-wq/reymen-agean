---
name: session-aware-qa
description: Any direct question from the user — factual, personal, or identity-based.
title: Session Aware Qa
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

sessions for previous identical or near-identical questions. When a repeat is found,
  acknowledge it and reference the previous answer instead of starting fresh. For
  answers that should be consistent (e.g. model identity), ensure the SAME answer
  is given every time.
# Session-Aware Q&A

## Trigger

Any direct question from the user — factual, personal, or identity-based.

## Steps

### 1. Check Current Conversation
Search backwards through the current conversation for the exact same (or very similar) question. If found:
- Acknowledge: "Bunu daha önce de sormuştun — [kısa cevap]"
- Give the same consistent answer as before — never contradict previous answers
- If the answer has changed legitimately (e.g. skill count that grew), explain WHY it changed

### 2. Check Past Sessions (session_search)
If NOT found in current conversation, use `session_search(query="user's question")` to check past sessions.
- Discovery shape: pass the question keywords, limit=3-5
- If a match is found, reference it: "Geçmiş oturumlarda da sormuştun — [özet]"
- Then give the answer (do NOT just say "check the past session" — provide the answer)

### 3. Answer Consistently
For identity questions ("Hangi modelsin", "Kimsin", etc.):
- Always give the EXACT same model identity string every time
- Example: "DeepSeek V4 Flash" — never "DeepSeek-Chat" on one turn and "DeepSeek V4 Flash" on another
- Include provider name for clarity

For data questions ("Kaç skill var", etc.):
- If the data may be dynamic, note the source and timestamp
- If the user asks again later and the data changed, explain what changed

## Pitfalls

- **Inconsistent identity answers**: Never call yourself "DeepSeek-Chat" in one turn and "DeepSeek V4 Flash" in another. Pick one canonical identity string and use it always.
- **Memory is not enough**: The user's preference to check past sessions was saved to memory, but the skill captures HOW to do it. Always run the session_search check before answering, not just rely on memory.
- **Don't fabricate past session results**: If session_search returns no results, say so honestly. Do not claim past context exists when it doesn't.
- **Don't be verbose about the check**: A brief acknowledgment ("Bunu daha önce de sormuştun") is enough — no need to explain the session_search mechanism unless asked.
- **Dynamic answers**: When the answer legitimately changes between asks (e.g. skill count), explain the change briefly ("Öncekinden farklı çünkü kütüphane genişlemiş").
