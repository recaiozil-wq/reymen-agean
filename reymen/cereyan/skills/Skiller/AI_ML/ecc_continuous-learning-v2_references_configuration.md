---
name: ecc_continuous-learning-v2_references_configuration
description: Configuration
title: "Ecc Continuous Learning V2 References Configuration"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Configuration |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Configuration

Edit `config.json` to control the background observer:

```json
{
  "version": "2.1",
  "observer": {
    "enabled": false,
    "run_interval_minutes": 5,
    "min_observations_to_analyze": 20
  }
}
```

| Key | Default | Description |
|-----|---------|-------------|
| `observer.enabled` | `false` | Enable the background observer agent |
| `observer.run_interval_minutes` | `5` | How often the observer analyzes observations |
| `observer.min_observations_to_analyze` | `20` | Minimum observations before analysis runs |

Other behavior (observation capture, instinct thresholds, project scoping, promotion criteria) is configured via code defaults in `instinct-cli.py` and `observe.sh`.
