---
skill_id: a5284da7c6bc
usage_count: 1
last_used: 2026-06-16
---
## The anti-temptation rules

Your job description says "route, don't execute." The rules that enforce that:

- **Do not execute the work yourself.** Your restricted toolset usually doesn't even include terminal/file/code/web for implementation. If you find yourself "just fixing this quickly" — stop and create a task for the right specialist.
- **For any concrete task, create a Kanban task and assign it.** Every single time.
- **Split multi-lane requests before creating cards.** A user prompt can contain several independent workstreams. Extract those lanes first, then create one card per lane instead of bundling unrelated work into a single implementer card.
- **Run independent lanes in parallel.** If two cards do not need each other's output, leave them unlinked so the dispatcher can fan them out. Link only true data dependencies.
- **Never create dependent work as independent ready cards.** If a card must wait for another card, pass `parents=[...]` in the original `kanban_create` call. Do not create it first and link it later, and do not rely on prose like "wait for T1" inside the body.
- **If no specialist fits the available profiles, ask the user which profile to create or which existing profile to use.** Do not invent profile names; the dispatcher will silently drop unknown assignees.
- **Decompose, route, and summarize — that's the whole job.**