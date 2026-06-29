---
name: ecc_logistics-exception-management_references_communication-patterns
description: Communication Patterns
title: "Ecc Logistics Exception Management References Communication Patterns"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_logistics-exception-management_references_communication-patterns.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## Communication Patterns

### Tone Calibration

Match communication tone to situation severity and relationship:

- **Routine exception, good carrier relationship:** Collaborative. "We've got a delay on PRO# X — can you get me an updated ETA? Customer is asking."
- **Significant exception, neutral relationship:** Professional and documented. State facts, reference BOL/PRO, specify what you need and by when.
- **Major exception or pattern, strained relationship:** Formal. CC management. Reference contract terms. Set response deadlines. "Per Section 4.2 of our transportation agreement dated..."
- **Customer-facing (delay):** Proactive, honest, solution-oriented. Never blame the carrier by name. "Your shipment has experienced a transit delay. Here's what we're doing and your updated timeline."
- **Customer-facing (damage/loss):** Empathetic, action-oriented. Lead with the resolution, not the problem. "We've identified an issue with your shipment and have already initiated [replacement/credit]."

### Key Templates

Brief templates appear below. Adapt them to your carrier, customer, and insurance workflows before using them in production.

**Initial carrier inquiry:** Subject: `Exception Notice — PRO# {pro} / BOL# {bol}`. State: what happened, what you need (ETA update, inspection, OS&D report), and by when.

**Customer proactive update:** Lead with: what you know, what you're doing about it, what the customer's revised timeline is, and your direct contact for questions.

**Escalation to carrier management:** Subject: `ESCALATION: Unresolved Exception — {shipment_ref} — {days} Days`. Include timeline of previous communications, financial impact, and what resolution you expect.
