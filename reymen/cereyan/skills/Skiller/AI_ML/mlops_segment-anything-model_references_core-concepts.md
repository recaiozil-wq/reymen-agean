---
name: mlops_segment-anything-model_references_core-concepts
description: Core concepts
title: "Mlops Segment Anything Model References Core Concepts"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Core concepts |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Core concepts

### Model architecture

<!-- ascii-guard-ignore -->
```
SAM Architecture:
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Image Encoder  │────▶│ Prompt Encoder  │────▶│  Mask Decoder   │
│     (ViT)       │     │ (Points/Boxes)  │     │ (Transformer)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
   Image Embeddings      Prompt Embeddings         Masks + IoU
   (computed once)       (per prompt)             predictions
```
<!-- ascii-guard-ignore-end -->

### Model variants

| Model | Checkpoint | Size | Speed | Accuracy |
|-------|------------|------|-------|----------|
| ViT-H | `vit_h` | 2.4 GB | Slowest | Best |
| ViT-L | `vit_l` | 1.2 GB | Medium | Good |
| ViT-B | `vit_b` | 375 MB | Fastest | Good |

### Prompt types

| Prompt | Description | Use Case |
|--------|-------------|----------|
| Point (foreground) | Click on object | Single object selection |
| Point (background) | Click outside object | Exclude regions |
| Bounding box | Rectangle around object | Larger objects |
| Previous mask | Low-res mask input | Iterative refinement |
