---
skill_id: f65c36d0c6e6
usage_count: 1
last_used: 2026-06-16
---
# Save final model
artifact = wandb.Artifact('final-model', type='model')
artifact.add_file('model.pth')
wandb.log_artifact(artifact)