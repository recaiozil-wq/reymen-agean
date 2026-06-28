---
skill_id: 37ea3d5172d9
usage_count: 1
last_used: 2026-06-16
---
# Deduplicate by URL
    seen, deduped = set(), []
    for item in all_items:
        if (url := item.get("url", "")) and url not in seen:
            seen.add(url); deduped.append(item)

    print(f"Unique items: {len(deduped)}")

    if ai_enabled() and deduped:
        from ai.memory import load_feedback, build_preference_prompt
        from ai.pipeline import analyse_batch