---
name: ecc_logistics-exception-management_references_decision-frameworks
description: Decision Frameworks
title: "Ecc Logistics Exception Management References Decision Frameworks"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_logistics-exception-management_references_decision-frameworks.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## Decision Frameworks

### Severity Classification

Assess every exception on three axes and take the highest severity:

**Financial Impact:**
- Level 1 (Low): < $1,000 product value, no expedite needed
- Level 2 (Moderate): $1,000 - $5,000 or minor expedite costs
- Level 3 (Significant): $5,000 - $25,000 or customer penalty risk
- Level 4 (Major): $25,000 - $100,000 or contract compliance risk
- Level 5 (Critical): > $100,000 or regulatory/safety implications

**Customer Impact:**
- Standard customer, no SLA at risk → does not elevate
- Key account with SLA at risk → elevate by 1 level
- Enterprise customer with penalty clauses → elevate by 2 levels
- Customer's production line or retail launch at risk → automatic Level 4+

**Time Sensitivity:**
- Standard transit with buffer → does not elevate
- Delivery needed within 48 hours, no alternative sourced → elevate by 1
- Same-day or next-day critical (production shutdown, event deadline) → automatic Level 4+

### Eat-the-Cost vs Fight-the-Claim

This is the most common judgment call. Thresholds:

- **< $500 and carrier relationship is strong:** Absorb. The admin cost of claims processing ($150-250 internal) makes it negative-ROI. Log for carrier scorecard.
- **$500 - $2,500:** File claim but don't escalate aggressively. This is the "standard process" zone. Accept partial settlements above 70% of value.
- **$2,500 - $10,000:** Full claims process. Escalate at 30-day mark if no resolution. Involve carrier account manager. Reject settlements below 80%.
- **> $10,000:** VP-level awareness. Dedicated claims handler. Independent inspection if damage. Reject settlements below 90%. Legal review if denied.
- **Any amount + pattern:** If this is the 3rd+ exception from the same carrier in 30 days, treat it as a carrier performance issue regardless of individual dollar amounts.

### Priority Sequencing

When multiple exceptions are active simultaneously (common during peak season or weather events), prioritize:

1. Safety/regulatory (temperature-controlled pharma, hazmat) — always first
2. Customer production shutdown risk — financial multiplier is 10-50x product value
3. Perishable with remaining shelf life < 48 hours
4. Highest financial impact adjusted for customer tier
5. Oldest unresolved exception (prevent aging beyond SLA)
