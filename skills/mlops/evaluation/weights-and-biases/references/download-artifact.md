---
skill_id: 2469a03f8b20
usage_count: 1
last_used: 2026-06-16
---
# Download artifact
artifact = run.use_artifact('training-dataset:latest')
artifact_dir = artifact.download()