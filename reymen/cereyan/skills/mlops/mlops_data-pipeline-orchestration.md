---
name: mlops_data-pipeline-orchestration
title: Data Pipeline Orchestration
description: "Design, build, and monitor data pipelines for ETL, feature engineering, and ML data preparation."
tags: [mlops, data-pipeline, etl, orchestration, data-engineering, airflow]
category: mlops
audience: agent
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Design, build, and monitor data pipelines for ETL, feature engineering, and ML data preparation. |
| **Nerede?** | mlops/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

# Data Pipeline Orchestration

## 🏗️ Pipeline Mimarisi

```
Veri Kaynakları           Processing              Storage/Hedef
──────────────────────────────────────────────────────────────
┌─────────┐    ┌─────────────┐    ┌──────────┐    ┌─────────┐
│ API     │───▶│ Extractor   │───▶│ Feature  │───▶│ Feature │
│ Streams │    │             │    │ Engineer │    │ Store   │
└─────────┘    └─────────────┘    └──────────┘    └─────────┘
┌─────────┐         │                  │
│ DB      │─────────┘                  │
└─────────┘                            │
┌─────────┐         │                  │
│ S3/GCS  │─────────┘                  │
└─────────┘                            │
                                       ▼
                              ┌─────────────────┐
                              │ Validator       │
                              │ (Quality Check) │
                              └────────┬────────┘
                                       │
                              ┌────────▼────────┐
                              │ Monitor & Alert │
                              └─────────────────┘
```

## 🔧 Pipeline Types

### Batch Pipeline (Airflow DAG)

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "mlops",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "ml_feature_pipeline",
    default_args=default_args,
    description="Daily ML feature engineering pipeline",
    schedule_interval="0 2 * * *",  # Her gün 02:00
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["ml", "features"],
) as dag:
    
    extract_raw_data = PostgresOperator(
        task_id="extract_raw_data",
        sql="sql/extract_raw_data.sql",
        postgres_conn_id="source_db",
    )
    
    validate_raw_data = PythonOperator(
        task_id="validate_raw_data",
        python_callable=lambda: validate_data_quality(
            table="raw_events",
            checks={
                "null_rate": {"threshold": 0.05, "column": "user_id"},
                "completeness": {"threshold": 0.95},
            }
        ),
    )
    
    def build_features(**context):
        import pandas as pd
        from datetime import datetime, timedelta
        
        # Raw data'yı yükle
        raw = pd.read_sql("SELECT * FROM raw_events WHERE date = CURRENT_DATE", ...)
        
        # Feature engineering
        features = pd.DataFrame()
        features["user_id"] = raw["user_id"]
        features["event_count_7d"] = raw.groupby("user_id")["event_id"].transform("count")
        features["avg_session_duration"] = raw.groupby("user_id")["duration"].transform("mean")
        features["last_active_hours"] = (datetime.now() - raw.groupby("user_id")["timestamp"].transform("max")).dt.total_seconds() / 3600
        
        # Save to feature store
        features.to_sql("user_features", ..., if_exists="append")
        
        return {"feature_count": len(features), "user_count": features["user_id"].nunique()}
    
    build_features_task = PythonOperator(
        task_id="build_features",
        python_callable=build_features,
    )
    
    monitor_pipeline = PythonOperator(
        task_id="monitor_pipeline",
        python_callable=lambda: log_pipeline_metrics(
            dag_id="ml_feature_pipeline",
            metrics={
                "features_generated": "{{ task_instance.xcom_pull(task_ids='build_features')['feature_count'] }}",
                "users_processed": "{{ task_instance.xcom_pull(task_ids='build_features')['user_count'] }}",
            }
        ),
    )
    
    # Dependencies
    extract_raw_data >> validate_raw_data >> build_features_task >> monitor_pipeline
```

### Streaming Pipeline (Kafka + Spark)

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Spark session setup
spark = SparkSession.builder \
    .appName("RealTimeFeaturePipeline") \
    .config("spark.sql.streaming.checkpointLocation", "/data/checkpoints") \
    .getOrCreate()

# Read from Kafka
raw_stream = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "user-events") \
    .load()

# Parse JSON
schema = StructType([
    StructField("user_id", StringType()),
    StructField("event_type", StringType()),
    StructField("timestamp", TimestampType()),
    StructField("properties", MapType(StringType(), StringType())),
])

events = raw_stream \
    .select(from_json(col("value").cast("string"), schema).alias("data")) \
    .select("data.*")

# Feature calculation
features = events \
    .withWatermark("timestamp", "1 hour") \
    .groupBy(
        window("timestamp", "1 hour"),
        "user_id",
        "event_type",
    ) \
    .agg(
        count("*").alias("event_count"),
        approx_count_distinct("properties").alias("unique_properties"),
    )

# Write to feature store
query = features \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", "false") \
    .start()

query.awaitTermination()
```

## 📊 Data Quality Validation

```python
def validate_data_quality(
    table: str,
    checks: dict,
    connection_id: str = "default",
) -> bool:
    """Run data quality checks on a table."""
    results = {"passed": [], "failed": []}
    
    for check_name, params in checks.items():
        if check_name == "null_rate":
            sql = f"""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN {params['column']} IS NULL THEN 1 ELSE 0 END) as nulls
                FROM {table}
            """
            row = execute_query(sql)
            null_rate = row["nulls"] / row["total"]
            
            if null_rate <= params["threshold"]:
                results["passed"].append(check_name)
            else:
                results["failed"].append({
                    "check": check_name,
                    "expected": f"null_rate <= {params['threshold']}",
                    "actual": f"null_rate = {null_rate:.3f}",
                })
        
        elif check_name == "completeness":
            sql = f"SELECT COUNT(*) as cnt FROM {table}"
            row = execute_query(sql)
            expected = int(row["total"] * params["threshold"])
            
            if row["cnt"] >= expected:
                results["passed"].append(check_name)
            else:
                results["failed"].append({
                    "check": check_name,
                    "expected": f">= {expected} rows",
                    "actual": f"{row['cnt']} rows",
                })
    
    if results["failed"]:
        send_alert(f"Data quality failed: {results['failed']}")
        return False
    
    return True
```

## 📋 Pipeline Monitoring

```python
def log_pipeline_metrics(dag_id: str, metrics: dict):
    """Log pipeline execution metrics."""
    from datetime import datetime
    
    log_entry = {
        "dag_id": dag_id,
        "timestamp": datetime.now().isoformat(),
        "metrics": metrics,
        "status": "success",
    }
    
    # Log to monitoring system
    # InfluxDB, Prometheus, or simple file log
    with open(f"/var/log/pipelines/{dag_id}.log", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    return log_entry
```

## 📋 Pipeline Checklist

### Design
- [ ] Data source reliability (retry, fallback)
- [ ] Idempotent processing (replay safe)
- [ ] Schema evolution handling
- [ ] Partition strategy (date, key)
- [ ] Monitoring & alerting

### Performance
- [ ] Batch size optimized
- [ ] Parallel processing where possible
- [ ] Memory management (GC tuning)
- [ ] Checkpointing for streaming

### Quality
- [ ] Data validation before processing
- [ ] Anomaly detection
- [ ] SLA monitoring (latency, throughput)
- [ ] Backfill capability
