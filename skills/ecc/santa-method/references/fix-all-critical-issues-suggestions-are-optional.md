---
skill_id: ecca6822a85a
usage_count: 1
last_used: 2026-06-16
---
# Fix all critical issues (suggestions are optional)
    output = fix_agent.execute(
        output=output,
        issues=issues,
        instruction="Fix ONLY the flagged issues. Do not refactor or add unrequested changes."
    )