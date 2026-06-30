---
name: mlops_model-deployment-pipeline
title: ML Model Deployment Pipeline
description: "Deploy ML models to production with serving infrastructure, A/B testing, monitoring, and rollback strategies."
tags: [mlops, deployment, models, serving, production, inference]
category: mlops
audience: agent
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Deploy ML models to production with serving infrastructure, A/B testing, monitoring, and rollback strategies. |
| **Nerede?** | mlops/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

# ML Model Deployment Pipeline

## 🏗️ Deployment Mimarisi

```
                         ┌──────────────┐
    Model Registry ─────▶│   Deployer    │◀────── CI/CD Trigger
                         └──────┬───────┘
                                │
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                  ▼
      ┌────────────┐   ┌────────────┐   ┌────────────┐
      │ Canary 5%  │   │ Staging    │   │ Production │
      └────────────┘   └────────────┘   └────────────┘
              │               │                │
              └───────────────┼────────────────┘
                              ▼
                     ┌──────────────┐
                     │   Monitor    │ ← Metrics, Drift, Latency
                     └──────┬───────┘
                            │
                     ┌──────▼───────┐
                     │   Alerting   │ → Rollback if P95 > 500ms
                     └──────────────┘
```

## 📦 Model Serving Options

| Araç | Kullanım | Avantaj | Dezavantaj |
|------|----------|---------|------------|
| **BentoML** | Python model serving | Full pipeline, monitoring | Heavy |
| **MLflow** | Model registry + serving | Integrated tracking | Limited scale |
| **TorchServe** | PyTorch models | Native PyTorch | Framework-specific |
| **Triton** | Multi-framework | GPU optimized | Complex setup |
| **SageMaker** | AWS managed | Auto-scaling | Vendor lock-in |
| **ONNX Runtime** | Cross-platform | Optimized inference | Opsiyonel |

## 🔧 Deployment Pipeline (Python)

```python
import bentoml
from bentoml.io import JSON, NumpyNdarray
import numpy as np
from typing import Any

# Model kaydetme
def save_model(model, model_name: str, version: str = None):
    """Model'i BentoML registry'e kaydet."""
    with bentoml.models.create(
        model_name,
        module=__name__,
        labels={
            "framework": "pytorch",
            "task": "classification",
            "version": version or "latest",
        },
    ) as ctx:
        ctx.model = model
    return f"{model_name}:{version or 'latest'}"

# Model serving API
@bentoml.service(
    name="model-serving",
    traffic={"timeout": 30, "max_concurrency": 100},
    resources={"memory": "2Gi", "cpu": "2"},
)
class ModelService:
    def __init__(self):
        self.model = bentoml.models.get("my_model:latest")
    
    @bentoml.api(input=JSON(), output=JSON())
    async def predict(self, input_data: dict) -> dict:
        features = np.array(input_data["features"])
        predictions = self.model.predict(features)
        return {
            "predictions": predictions.tolist(),
            "model_version": "latest",
            "status": "success",
        }
    
    @bentoml.api(input=JSON(), output=JSON())
    async def health(self) -> dict:
        return {"status": "healthy", "model_loaded": True}
```

## 🔄 A/B Testing & Canary Deployment

```python
# Canary deployment logic
class CanaryDeployer:
    def __init__(self):
        self.canary_percent = 5  # Start with 5%
        self.step = 5            # Increase by 5%
        self.max_percent = 50    # Max canary
        
    def should_route_to_canary(self, user_id: str) -> bool:
        hash_val = hash(user_id) % 100
        return hash_val < self.canary_percent
    
    def promote_if_healthy(self, metrics: dict) -> bool:
        """Canary'i promote et veya rollback yap."""
        if metrics.get("error_rate", 0) > 0.01:
            self.rollback()
            return False
        
        if metrics.get("p95_latency_ms", 0) > 500:
            self.rollback()
            return False
        
        self.canary_percent = min(
            self.canary_percent + self.step,
            self.max_percent
        )
        return True
```

## 📊 Monitoring & Alerting

```python
# Model monitoring metrics
def collect_model_metrics(model_version: str) -> dict:
    return {
        "version": model_version,
        "latency_p50": get_percentile("latency", 50),
        "latency_p95": get_percentile("latency", 95),
        "latency_p99": get_percentile("latency", 99),
        "error_rate": count_errors() / total_requests(),
        "throughput": requests_per_second(),
        "prediction_distribution": get_prediction_stats(),
        "data_drift_score": calculate_drift(),
        "model_version": model_version,
    }

# Alert thresholds
ALERT_THRESHOLDS = {
    "latency_p95": {"warn": 300, "critical": 500},       # ms
    "error_rate": {"warn": 0.01, "critical": 0.05},      # 1%-5%
    "data_drift": {"warn": 0.3, "critical": 0.5},         # PSI/KL
    "throughput_drop": {"warn": 0.2, "critical": 0.5},    # 20%-50%
}
```

## 📋 Deployment Checklist

### Pre-deployment
- [ ] Model validation passed (accuracy > threshold)
- [ ] Data drift check on latest data
- [ ] Bias/fairness test passed
- [ ] Model size optimized (quantization, pruning)
- [ ] Batch inference support (if needed)
- [ ] Load test completed (1000 req/s for 5 min)

### Deployment
- [ ] Canary deployment (5% traffic)
- [ ] Monitor for 10 minutes
- [ ] Gradual rollout (25% → 50% → 100%)
- [ ] Old version kept for rollback (24h)

### Post-deployment
- [ ] Shadow mode for 1 day (compare old vs new)
- [ ] Performance dashboard updated
- [ ] Alerts configured
- [ ] Rollback procedure documented
