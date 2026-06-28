
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Kanban Orchestrator_References_Goal Mode Cards Persistent Workers |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## Goal-mode cards (persistent workers)

By default a dispatched worker gets **one shot** at its card: it does its work, calls `kanban_complete`/`kanban_block`, and exits. For open-ended cards where one turn rarely finishes the job, pass `goal_mode=True` to wrap that worker in a Ralph-style goal loop — the same engine behind the `/goal` slash command:

```python
kanban_create(
    title="Translate the full docs site to French",
    body="Acceptance: every page translated, no English left, links intact.",
    assignee="<translator-profile>",
    goal_mode=True,        # judge re-checks the card after each turn
    goal_max_turns=15,     # optional budget (default 20)
)["task_id"]
```

How it behaves:
- After each worker turn, an auxiliary judge evaluates the worker's response against the card's **title + body** (treated as the acceptance criteria).
- Not done + budget remains → the worker keeps going **in the same session** (full context retained — not a fresh respawn).
- Worker calls `kanban_complete`/`kanban_block` itself → loop stops, normal lifecycle.
- Budget exhausted without completion → the card is **blocked** for human review (sticky), never a silent exit.

When to use it: long, multi-step, or "keep going until X is true" cards. When NOT to: cheap one-shot cards (translation of a single string, a quick lookup) — the judge overhead isn't worth it, and the dispatcher's existing retry/circuit-breaker already handles transient worker failures.

Write the body as **explicit acceptance criteria** — the judge is only as good as the goal text. "Translate the README" is weaker than "Translate every section of the README to French; no English sentences remain."