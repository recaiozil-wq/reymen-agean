---
name: ecc_lead-intelligence_references_step-2-exa-deep-search-for-people
description: "Step 2: Exa deep search for people"
title: "Ecc Lead Intelligence References Step 2 Exa Deep Search For People"
version: 1.0.0
---

| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** |  |
| **Nerede** | `AI_ML/ecc_lead-intelligence_references_step-2-exa-deep-search-for-people.md` |
| **Ne Zaman** |  |
| **Neden** |  |
| **Nasıl** |  |

# Step 2: Exa deep search for people
for vertical in target_verticals:
    results = web_search_exa(
        query=f"{vertical} {role} founder CEO",
        category="company",
        numResults=20
    )
