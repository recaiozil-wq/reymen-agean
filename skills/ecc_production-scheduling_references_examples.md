---
name: ecc_production-scheduling_references_examples
description: Examples
title: "Ecc Production Scheduling References Examples"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Examples |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Examples

- **Constraint breakdown**: Line 2 CNC machine goes down for 4 hours. Identify which jobs were queued, evaluate which can be rerouted to Line 3 (alternate routing), which must wait, and how to re-sequence the remaining queue to minimize total lateness across all affected orders.
- **Campaign vs. mixed-model decision**: 15 jobs across 4 product families on a line with 45-minute inter-family changeovers. Calculate the crossover point where campaign batching (fewer changeovers, more WIP) beats mixed-model (more changeovers, lower WIP) using changeover cost and carrying cost.
- **Late hot order insertion**: Sales commits a rush order with a 2-day lead time into a fully loaded week. Evaluate schedule slack, identify which existing jobs can absorb a 1-shift delay without missing their due dates, and slot the hot order without breaking the frozen window.
