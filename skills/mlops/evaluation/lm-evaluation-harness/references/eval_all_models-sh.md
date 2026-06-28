---
skill_id: c4e19470f5b6
usage_count: 1
last_used: 2026-06-16
---
# eval_all_models.sh

TASKS="mmlu,gsm8k,hellaswag,truthfulqa"

while read model; do
    echo "Evaluating $model"