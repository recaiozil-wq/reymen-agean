---
name: mlops_experiment-tracking
title: ML Experiment Tracking & Management
description: "Track ML experiments, hyperparameters, metrics, artifacts, and model versions with reproducible results."
tags: [mlops, experiments, tracking, mlflow, reproducibility, hyperparameters]
category: mlops
audience: agent
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Track ML experiments, hyperparameters, metrics, artifacts, and model versions with reproducible results. |
| **Nerede?** | mlops/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

# ML Experiment Tracking & Management

## 📊 Experiment Tracking Stack

```
                          ┌──────────────┐
                          │  MLflow       │  ← Experiment tracking
                          │  Tracking     │
                          └──────┬───────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        ▼                        ▼                        ▼
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│ Parameters    │       │   Metrics    │       │  Artifacts   │
│ - learning    │       │ - accuracy   │       │ - models     │
│   rate: 0.001 │       │ - loss: 0.05 │       │ - plots      │
│ - batch: 32   │       │ - f1: 0.92   │       │ - datasets   │
│ - optimizer   │       │ - precision  │       │ - logs       │
└──────────────┘       └──────────────┘       └──────────────┘
```

## 🔧 MLflow Setup

```bash
# MLflow kurulumu
pip install mlflow mlflow[extras]

# MLflow tracking server
mlflow server \
    --backend-store-uri sqlite:///mlflow.db \
    --default-artifact-root ./mlruns \
    --host 0.0.0.0 \
    --port 5000
```

## 📝 Experiment Tracking Template

```python
import mlflow
import mlflow.sklearn
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib

def run_experiment(
    experiment_name: str,
    model_class,
    X_train, X_test, y_train, y_test,
    **hyperparams,
):
    """ML experiment with full tracking."""
    
    # Experiment setup
    mlflow.set_experiment(experiment_name)
    
    with mlflow.start_run() as run:
        run_id = run.info.run_id
        print(f"Run ID: {run_id}")
        
        # 1. Log parameters
        mlflow.log_params(hyperparams)
        mlflow.log_param("model_type", model_class.__name__)
        mlflow.log_param("train_samples", len(X_train))
        mlflow.log_param("test_samples", len(X_test))
        
        # 2. Train model
        model = model_class(**hyperparams)
        model.fit(X_train, y_train)
        
        # 3. Evaluate
        y_pred = model.predict(X_test)
        
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, average="weighted"),
            "recall": recall_score(y_test, y_pred, average="weighted"),
            "f1": f1_score(y_test, y_pred, average="weighted"),
        }
        
        # 4. Log metrics
        mlflow.log_metrics(metrics)
        
        # 5. Log model
        mlflow.sklearn.log_model(model, "model")
        
        # 6. Log additional artifacts
        with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as f:
            joblib.dump(model, f.name)
            mlflow.log_artifact(f.name, "models")
        
        # 7. Log dataset info
        mlflow.log_text(
            f"Features: {list(X_train.columns)}\nTarget: {y_train.name}",
            "dataset_info.txt"
        )
        
        return {
            "run_id": run_id,
            "metrics": metrics,
            "model": model,
        }
```

## 🔄 Experiment Organization

```python
# Experiment hierarchy
def organize_experiments(base_name: str, variants: list[str]):
    """Organize experiments by variant for comparison."""
    for variant in variants:
        experiment_name = f"{base_name}_{variant}"
        mlflow.set_experiment(experiment_name)
        
        # Tag for grouping
        mlflow.set_tag("experiment_group", base_name)
        mlflow.set_tag("variant", variant)
```

## 📋 Experiment Comparison

```python
# MLflow API ile karşılaştırma
def compare_experiments(experiment_name: str) -> list[dict]:
    """Compare all runs in an experiment."""
    client = mlflow.tracking.MlflowClient()
    experiment = client.get_experiment_by_name(experiment_name)
    
    runs = mlflow.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["metrics.f1 DESC"],
    )
    
    return [
        {
            "run_id": row["run_id"],
            "params": {k: v for k, v in row.items() if k.startswith("params.")},
            "metrics": {k: v for k, v in row.items() if k.startswith("metrics.")},
            "status": row["status"],
        }
        for _, row in runs.iterrows()
    ]
```

## 🏆 Model Registry

```python
def register_best_model(
    experiment_name: str,
    model_name: str,
    metric: str = "metrics.f1",
):
    """Find and register the best model."""
    client = mlflow.tracking.MlflowClient()
    
    # Best run'ı bul
    runs = mlflow.search_runs(
        experiment_names=[experiment_name],
        order_by=[f"{metric} DESC"],
        max_results=1,
    )
    
    if runs.empty:
        raise ValueError(f"No runs found for experiment: {experiment_name}")
    
    best_run = runs.iloc[0]
    run_id = best_run["run_id"]
    
    # Model registry'e register et
    result = mlflow.register_model(
        f"runs:/{run_id}/model",
        model_name,
    )
    
    # Stage tag ekle
    client.transition_model_version_stage(
        name=model_name,
        version=result.version,
        stage="Staging",
    )
    
    return {
        "run_id": run_id,
        "model_name": model_name,
        "version": result.version,
        "stage": "Staging",
    }
```

## 📊 Visualization

```python
# MLflow ile görselleştirme
def log_training_curves(history: dict, prefix: str = ""):
    """Log training curves as MLflow artifacts."""
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    
    # Loss curve
    axes[0].plot(history["train_loss"], label="Train Loss")
    axes[0].plot(history["val_loss"], label="Val Loss")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Loss")
    axes[0].legend()
    axes[0].grid(True)
    
    # Accuracy curve
    axes[1].plot(history["train_acc"], label="Train Acc")
    axes[1].plot(history["val_acc"], label="Val Acc")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("Accuracy")
    axes[1].legend()
    axes[1].grid(True)
    
    plt.tight_layout()
    
    # Save and log
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        plt.savefig(f.name, dpi=150, bbox_inches="tight")
        mlflow.log_artifact(f.name, "plots")
    
    plt.close()
```

## 📋 Best Practices

| Uygulama | Açıklama |
|----------|----------|
| **Her run unique** | Tüm denemeleri logla, başarısız olsa bile |
| **Seed kaydet** | random_state, numpy seed logla |
| **Environment log** | `mlflow.log_artifact("requirements.txt")` |
| **Dataset hash** | Veri seti hash'ini logla |
| **Tags kullan** | Ekiplere göre etiketle |
| **Parent/child runs** | Hiperparametre aramalarını grupla |
| **Artefaktları temizle** | Başarısız run'ların artefaktlarını sil |
