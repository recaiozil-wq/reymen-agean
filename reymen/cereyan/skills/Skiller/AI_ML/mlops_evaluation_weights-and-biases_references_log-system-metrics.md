---
name: mlops_evaluation_weights-and-biases_references_log-system-metrics
description: Log system metrics
title: "Mlops Evaluation Weights And Biases References Log System Metrics"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Log system metrics |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Log system metrics
wandb.log({
    "gpu/util": gpu_utilization,
    "gpu/memory": gpu_memory_used,
    "cpu/util": cpu_utilization
})
