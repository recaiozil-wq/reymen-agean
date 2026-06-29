---
name: mlops_evaluation_weights-and-biases_references_download-artifact
description: Download artifact
title: "Mlops Evaluation Weights And Biases References Download Artifact"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Download artifact |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Download artifact
artifact = run.use_artifact('training-dataset:latest')
artifact_dir = artifact.download()
