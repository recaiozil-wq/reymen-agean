---
name: virtual-memory
description: Virtual Memory skill for AI/ML operations.
title: Virtual Memory
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

store + memory tools) for any target runtime with correct eviction, citation, and
  untrusted-input handling.
Given a target runtime (Python, Node, Rust), a model provider (Anthropic, OpenAI, local), and a storage backend (in-memory, SQLite, vector DB, KV, graph), produce a correct MemGPT-shaped memory system.
1. A `MainContext` type with a `core` dict (named persistent sections) and a `messages` list (FIFO). Auto-evict on size cap; evicted turns remain retrievable by `conversation_search`.
2. An `ArchivalStore` with insert and search. Records MUST carry `id`, `text`, `tags`, `session_id`, `turn_id`, `created_at`. Every write returns the stored id for citation.
3. Five memory tools matching the MemGPT surface: `core_memory_append`, `core_memory_replace`, `archival_memory_insert`, `archival_memory_search`, `conversation_search`. Present them to the model with `description` text that tells the model when to use each.
4. A citation contract: every archival retrieval MUST return record ids alongside text, and the agent MUST cite them in final answers. Answers without citations are a soft failure.
5. A consolidation hook (can be a no-op in v1) so Lesson 08 sleep-time agents can plug in without re-plumbing. Expose `list_records_since(timestamp)` and `delete(id)`.
Hard rejects:
- Searching archival with full-prompt LLM scoring. Use a proper retrieval backend (BM25, vector similarity). LLM re-ranking is allowed on the top-k shortlist, not the full corpus.
- Main context with no eviction policy. Unbounded main context silently grows past the window.
- Storing retrieved content as if it were user instructions. All archival content is untrusted text (Lesson 27). Pass it to the model as observation, not as system prompt.
- Writing a `core_memory_clear` tool that wipes all sections. Core is load-bearing; clearing is a foot-gun. Support `replace` not `clear`.
Refusal rules:
- If the user asks for "no citations, just answers," refuse for any domain where source attribution matters (medical, legal, policy, financial). Offer a compromise: citations rendered as footnotes rather than inline.
- If the user asks for "write all retrieved content back to archival without filtering," refuse and point to Lesson 27. Retrieved content is attacker-reachable; blanket write-back is memory poisoning.
- If the runtime has no persistence layer, refuse to ship an agent described as having "long-term memory." Downgrade the product description, not the implementation.
