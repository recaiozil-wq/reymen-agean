---
name: ecc_lead-intelligence_references_stage-1-signal-scoring
description: "Stage 1: Signal Scoring"
title: "Ecc Lead Intelligence References Stage 1 Signal Scoring"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_lead-intelligence_references_stage-1-signal-scoring.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

## Stage 1: Signal Scoring

Search for high-signal people in target verticals. Assign a weight to each based on:

| Signal | Weight | Source |
|--------|--------|--------|
| Role/title alignment | 30% | Exa, LinkedIn |
| Industry match | 25% | Exa company search |
| Recent activity on topic | 20% | X API search, Exa |
| Follower count / influence | 10% | X API |
| Location proximity | 10% | Exa, LinkedIn |
| Engagement with your content | 5% | X API interactions |

### Signal Search Approach

```python
