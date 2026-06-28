---
skill_id: 8db7707cb791
usage_count: 1
last_used: 2026-06-16
---
# Step 2: Exa deep search for people
for vertical in target_verticals:
    results = web_search_exa(
        query=f"{vertical} {role} founder CEO",
        category="company",
        numResults=20
    )