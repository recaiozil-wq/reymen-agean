---
name: ecc_production-scheduling_references_escalation-protocols
description: Escalation Protocols
title: "Ecc Production Scheduling References Escalation Protocols"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Escalation Protocols |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Escalation Protocols

### Automatic Escalation Triggers

| Trigger | Action | Timeline |
|---|---|---|
| Constraint work centre down > 30 minutes unplanned | Alert production manager + maintenance manager | Immediate |
| Plan adherence drops below 80% for a shift | Root cause analysis with shift supervisor | Within 4 hours |
| Customer order projected to miss committed ship date | Notify sales and customer service with revised ETA | Within 2 hours of detection |
| Overtime requirement exceeds weekly budget by > 20% | Escalate to plant manager with cost-benefit analysis | Within 1 business day |
| OEE at constraint drops below 65% for 3 consecutive shifts | Trigger focused improvement event (maintenance + engineering + scheduling) | Within 1 week |
| Quality yield at constraint drops below 93% | Joint review with quality engineering | Within 24 hours |
| MRP-generated load exceeds finite capacity by > 15% for the upcoming week | Capacity meeting with planning and production management | 2 days before the overloaded week |

### Escalation Chain

Level 1 (Production Scheduler) → Level 2 (Production Manager / Shift Superintendent, 30 min for constraint issues, 4 hours for non-constraint) → Level 3 (Plant Manager, 2 hours for customer-impacting issues) → Level 4 (VP Operations, same day for multi-customer impact or safety-related schedule changes)
