---
skill_id: a1385dae6de6
usage_count: 1
last_used: 2026-06-16
---
# Training arguments with W&B
training_args = TrainingArguments(
    output_dir="./results",
    report_to="wandb",  # Enable W&B logging
    run_name="bert-finetuning",
    logging_steps=100,
    save_steps=500
)