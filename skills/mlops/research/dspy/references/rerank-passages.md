---
skill_id: adb36890ae64
usage_count: 1
last_used: 2026-06-16
---
# Rerank passages
        scored = []
        for passage in passages:
            score = float(self.rerank(question=question, passage=passage).relevance_score)
            scored.append((score, passage))