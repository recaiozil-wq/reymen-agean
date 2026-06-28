---
name: ecc_santa-method_references_both-run-concurrently-neither-sees-the-other
description: Both run concurrently — neither sees the other
title: "Ecc Santa Method References Both Run Concurrently Neither Sees The Other"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Both run concurrently — neither sees the other |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Both run concurrently — neither sees the other
```

### Rubric Design

The rubric is the most important input. Vague rubrics produce vague reviews. Every criterion must have an objective pass/fail condition.

| Criterion | Pass Condition | Failure Signal |
|-----------|---------------|----------------|
| Factual accuracy | All claims verifiable against source material or common knowledge | Invented statistics, wrong version numbers, nonexistent APIs |
| Hallucination-free | No fabricated entities, quotes, URLs, or references | Links to pages that don't exist, attributed quotes with no source |
| Completeness | Every requirement in the spec is addressed | Missing sections, skipped edge cases, incomplete coverage |
| Compliance | Passes all project-specific constraints | Banned terms used, tone violations, regulatory non-compliance |
| Internal consistency | No contradictions within the output | Section A says X, section B says not-X |
| Technical correctness | Code compiles/runs, algorithms are sound | Syntax errors, logic bugs, wrong complexity claims |

#### Domain-Specific Rubric Extensions

**Content/Marketing:**
- Brand voice adherence
- SEO requirements met (keyword density, meta tags, structure)
- No competitor trademark misuse
- CTA present and correctly linked

**Code:**
- Type safety (no `any` leaks, proper null handling)
- Error handling coverage
- Security (no secrets in code, input validation, injection prevention)
- Test coverage for new paths

**Compliance-Sensitive (regulated, legal, financial):**
- No outcome guarantees or unsubstantiated claims
- Required disclaimers present
- Approved terminology only
- Jurisdiction-appropriate language

### Phase 3: Naughty or Nice (Verdict Gate)

```python
def santa_verdict(review_b, review_c):
    """Both reviewers must pass. No partial credit."""
    if review_b.verdict == "PASS" and review_c.verdict == "PASS":
        return "NICE"  # Ship it
