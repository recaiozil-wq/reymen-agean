---
skill_id: e8528a695e13
usage_count: 1
last_used: 2026-06-16
---
# Take top 3
        top_passages = [p for _, p in sorted(scored, reverse=True)[:3]]
        context = "\n\n".join(top_passages)