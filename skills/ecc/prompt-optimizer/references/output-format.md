---
skill_id: 1e086202b692
usage_count: 1
last_used: 2026-06-16
---
## Output Format

Present your analysis in this exact structure. Respond in the same language
as the user's input.

### Section 1: Prompt Diagnosis

**Strengths:** List what the original prompt does well.

**Issues:**

| Issue | Impact | Suggested Fix |
|-------|--------|---------------|
| (problem) | (consequence) | (how to fix) |

**Needs Clarification:** Numbered list of questions the user should answer.
If Phase 0 auto-detected the answer, state it instead of asking.

### Section 2: Recommended ECC Components

| Type | Component | Purpose |
|------|-----------|---------|
| Command | /plan | Plan architecture before coding |
| Skill | tdd-workflow | TDD methodology guidance |
| Agent | code-reviewer | Post-implementation review |
| Model | Sonnet 4.6 | Recommended for this scope |

### Section 3: Optimized Prompt — Full Version

Present the complete optimized prompt inside a single fenced code block.
The prompt must be self-contained and ready to copy-paste. Include:
- Clear task description with context
- Tech stack (detected or specified)
- /command invocations at the right workflow stages
- Acceptance criteria
- Verification steps
- Scope boundaries (what NOT to do)

For items that reference blueprint, write: "Use the blueprint skill to..."
(not `/blueprint`, since blueprint is a skill, not a command).

### Section 4: Optimized Prompt — Quick Version

A compact version for experienced ECC users. Vary by intent type:

| Intent | Quick Pattern |
|--------|--------------|
| New Feature | `/plan [feature]. /tdd to implement. /code-review. /verify.` |
| Bug Fix | `/tdd — write failing test for [bug]. Fix to green. /verify.` |
| Refactor | `/refactor-clean [scope]. /code-review. /verify.` |
| Research | `Use search-first skill for [topic]. /plan based on findings.` |
| Testing | `/tdd [module]. /e2e for critical flows. /test-coverage.` |
| Review | `/code-review. Then use security-reviewer agent.` |
| Docs | `/update-docs. /update-codemaps.` |
| EPIC | `Use blueprint skill for "[objective]". Execute phases with /verify gates.` |

### Section 5: Enhancement Rationale

| Enhancement | Reason |
|-------------|--------|
| (what was added) | (why it matters) |

### Footer

> Not what you need? Tell me what to adjust, or make a normal task request
> if you want execution instead of prompt optimization.

---