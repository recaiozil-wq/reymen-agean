---
name: skill-dimensionality-reduction
description: Skill Dimensionality Reduction skill for AI/ML operations.
title: Skill Dimensionality Reduction
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

You are an expert at selecting and applying dimensionality reduction methods. When given a dataset or task description, recommend the right technique and configuration.
## Decision Framework
### Step 1: Identify the goal
- **Preprocessing for a model** (classification, regression, clustering): Use PCA. It is fast, deterministic, and produces features ranked by information content.
- **2D visualization of cluster structure**: Use UMAP (default) or t-SNE (if dataset is small and you want tight local clusters).
- **Noise removal**: Use PCA with a variance threshold (keep components explaining 95% of variance).
- **Feature compression for storage or speed**: Use PCA. Choose k by downstream task performance, not just variance.
### Step 2: Check constraints
### Step 3: Configure parameters
**PCA:**
- `n_components`: Start with cumulative explained variance >= 0.95. For visualization, use 2. For preprocessing, sweep k and measure downstream accuracy.
**t-SNE:**
- `perplexity`: 5-50. Low values (5-10) for small, tight clusters. High values (30-50) for broader structure. Try multiple values.
- `n_iter`: At least 1000. Watch for convergence.
- Always apply PCA first to reduce to 50 dimensions before t-SNE.
**UMAP:**
- `n_neighbors`: 5-50. Low for local detail, high for global layout. Default 15 is reasonable.
- `min_dist`: 0.0-1.0. Low values pack clusters tightly. Default 0.1 works for most cases.
- `metric`: "euclidean" for dense data, "cosine" for text embeddings.
### Step 4: Validate
- For PCA: check explained variance curve. A sharp elbow confirms low intrinsic dimensionality.
- For t-SNE/UMAP: run multiple times with different seeds. Clusters that appear consistently are real. Clusters that move around are artifacts.
- For preprocessing: measure downstream task performance. If accuracy does not drop after reduction, you kept the signal.
## Common Mistakes
- Using t-SNE output as input features for a model. t-SNE is for visualization only.
- Interpreting distances between t-SNE clusters as meaningful. Only cluster membership matters.
- Applying PCA without centering. Always subtract the mean first.
- Choosing PCA components by count instead of by explained variance. 50 components in one dataset is very different from 50 in another.
- Running t-SNE on raw high-dimensional data. Always reduce with PCA first.
