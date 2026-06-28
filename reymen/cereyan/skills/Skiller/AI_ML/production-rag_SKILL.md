---
name: production-rag
description: Production Rag skill for AI/ML operations.
title: Production Rag
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

prompt caching, guardrails, and live drift monitoring.
Given a regulated-domain corpus (legal contracts, clinical trial protocols, insurance policies, or similar), deploy a chatbot that answers with verifiable citations, respects role and jurisdiction access policies, and is monitored for drift.
Build plan:
1. Parse the corpus with docling or Unstructured; route visually rich documents through ColPali. Emit chunks with role and jurisdiction labels.
2. Index dense (Voyage-3 or Nomic-embed-v2) into pgvector + pgvectorscale; sparse BM25 via Tantivy.
3. Wire LangGraph conversational agent: retrieve (filter by role + jurisdiction, hybrid dense+BM25, reciprocal rank fusion), rerank (bge-reranker-v2-gemma-2b or Voyage rerank-2), synth (Claude Sonnet 4.7 with prompt caching).
4. Assemble prompts with stable prefixes: system preamble -> policy block -> reranked context -> user query. Target 60-80% prompt-cache hit rate.
5. Guardrails: Llama Guard 4 on input and output, NeMo Guardrails v0.12 rails for off-domain and policy-forbidden questions, Presidio PII scrub on output, citation enforcement post-filter.
6. Build a 200-question expert-labeled golden set with (answer, citations). Score on exact-citation match, answer correctness, RAGAS faithfulness.
7. Build a 50-prompt red team (PAIR, TAP, PII extraction, off-domain, cross-jurisdiction probes).
8. Arize Phoenix drift dashboard tracking retrieval nDCG and citation faithfulness weekly; alert on 5% drop.
9. Langfuse cost report: prompt-cache hit rate, tokens per query, $/query by stage.
Assessment rubric:
Hard rejects:
- Any chatbot that leaks cross-jurisdiction data. Role+jurisdiction filtering must be enforced before retrieval, not after.
- Synthesis prompts that break cache prefixes (reordering policy between system and context). Will destroy the cache economics.
- Guardrail configurations without logged red-team runs.
- Answers without citations; citations without verifiable anchors.
Refusal rules:
- Refuse to deploy in a regulated domain without jurisdiction tags on every chunk.
- Refuse to train retrieval on expert-labeled golden set questions. Contamination destroys eval credibility.
- Refuse to claim "compliant" without an explicit SOC2/HIPAA/GDPR applicability matrix in the README.
