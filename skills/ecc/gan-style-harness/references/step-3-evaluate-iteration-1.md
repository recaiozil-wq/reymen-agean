---
skill_id: e89a43c29182
usage_count: 1
last_used: 2026-06-16
---
# Step 3: Evaluate (iteration 1)
claude -p --model opus --allowedTools "Read,Bash,mcp__playwright__*" "You are an Evaluator. Read EVALUATOR_PROMPT.md. Test the live app at http://localhost:3000. Score against the rubric. Write feedback to feedback-001.md"