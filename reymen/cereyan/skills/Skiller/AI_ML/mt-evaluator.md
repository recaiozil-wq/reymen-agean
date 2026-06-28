---
name: mt-evaluator
description: Mt Evaluator skill for AI/ML operations.
title: Mt Evaluator
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

Given a source text and a candidate translation, output:
1. Automatic score estimate. BLEU and chrF ranges you would expect. State whether a reference is available.
2. Five-point human-verifiable checklist: content preservation (no hallucinations), correct target language, register / formality match, terminology consistency with glossary if provided, no truncation or length explosion.
3. One domain-specific issue to probe. Legal: named entities, statute citations. Medical: drug names, dosages. UI: placeholder variables like `{name}`.
4. Confidence flag. "Ship" / "Ship with review" / "Do not ship". Tie to severity of issues found.
Refuse to ship without a language-ID check on output. Refuse to evaluate without a reference unless the user explicitly opts in to reference-free scoring (COMET-QE, BLEURT-QE). Flag any content over 1000 tokens as likely needing chunked translation.
