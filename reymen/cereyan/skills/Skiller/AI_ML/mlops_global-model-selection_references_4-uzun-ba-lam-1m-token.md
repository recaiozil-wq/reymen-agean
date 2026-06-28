---
name: mlops_global-model-selection_references_4-uzun-ba-lam-1m-token
description: 4.
title: "Mlops Global Model Selection References 4 Uzun Ba Lam 1M Token"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | 4.0 |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## 4. UZUN BAĞLAM (1M Token)

| Görev | En İyi Model | Skor | 2. Seçenek | Skor |
|-------|-------------|------|-----------|------|
| **MRCR 1M (belge okuma)** | **Opus 4.8** | **%92.9** | Fable 5 | %89.5 |
| **CorpusQA 1M (külliyat)** | **Opus 4.8** | **%71.7** | Fable 5 | %68.2 |
| **GraphWalks BFS 256K** | **Fable 5** | **%91.1** | Opus 4.8 | %85.9 |
| **GraphWalks Parents 256K** | **Fable 5** | **%99.96** | Opus 4.8 | %99.9 |

> MRCR/CorpusQA'da Opus 4.8 lider, GraphWalks'ta Fable 5 önde.
> Uzun belge + karmaşık ilişki → **Fable 5**. Düz okuma → **Opus 4.8**.
