---
name: ecc_plan-orchestrate_references_how-it-works
description: How It Works
title: "Ecc Plan Orchestrate References How It Works"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | How It Works |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## How It Works

### Phase 0 — Detect ECC mode + language

1. Read `<plan-doc-path>`. If missing or empty, report and stop.
2. Detect ECC install form once and freeze it into `ECC_MODE`. Algorithm (run in order, stop at the first match):
   1. If `<claude-home>/plugins/marketplaces/everything-claude-code/` exists → `ECC_MODE=plugin`.
   2. Else if `<claude-home>/agents/` exists and contains at least one ECC agent file (e.g. `tdd-guide.md`, `code-reviewer.md`) → `ECC_MODE=legacy`.
   3. Else → default to `ECC_MODE=legacy` and emit a one-line warning at the top of the output: `> Warning: could not detect ECC install; defaulting to legacy form. If you use the plugin install, edit the prefixes manually.`
   4. If both markers exist (mixed install), `plugin` wins — the plugin namespace is the only one that resolves agent names without fuzzy matching.

   From this point on, every emitted line uses the matching prefix on **both** the slash command and every agent name. **Never emit both forms in the same output.**
3. Resolve `--lang`. When `auto`, run a polyglot-aware detection:
   - Probe markers: `pyproject.toml` / `uv.lock` / `requirements.txt` → python; `package.json` → typescript; `go.mod` → go; `Cargo.toml` → rust; `CMakeLists.txt` or top-level `*.cpp` → cpp; `pom.xml` / `build.gradle` (Java) → java; `build.gradle.kts` or top-level Kotlin → kotlin; `pubspec.yaml` → flutter.
   - **Polyglot tie-break**: if more than one marker matches, pick the language whose source files outnumber the others (count via `git ls-files`, excluding `vendor/`, `node_modules/`, `dist/`, `build/`, `.venv/`, generated files, and obvious test fixtures). On a tie or when no language exceeds 60% of source files, set `lang=unknown`.
   - No marker matched → set `lang=unknown`.
   - `lang=unknown` is a sentinel — it is **not** an agent name. Phase 2 rules 4 and 5 turn it into `code-reviewer` / `build-error-resolver` at chain composition time.
4. Detect a **PyTorch sub-profile**: when `lang=python` and any of `pyproject.toml` / `requirements.txt` / `uv.lock` declares a dependency on `torch`, set `pytorch=true`. This only affects `build` chain selection (Phase 2 rule below); the reviewer remains `python-reviewer`.
5. **Normalize any agent names declared in the plan**: if the plan text references agents by their plugin-prefixed form (e.g. `everything-claude-code:tdd-guide`), strip the prefix to get the bare catalogue name before validating or composing chains. Re-prefixing happens only at output time per `ECC_MODE` (Phase 4). Never let a pre-prefixed name flow into chain composition — it would double-prefix in plugin mode.

### Phase 1 — Decompose steps

Identify "step units" in priority order:

1. Explicit numbering: `## Step N` / `### Phase N` / `## N. ...` / top-level ordered list.
2. A "Step" column in a table.
3. `---`-separated blocks with verb-led headings.
4. Otherwise treat each H2 as one step.

Per step extract `id` (1-based), `title` (≤ 80 chars), `intent` (1–3 sentences), `tags`.

### Phase 2 — Tag and pick chain

Tag by intent (multi-tag allowed; chain built from primary + stacked secondaries):

Trigger words below are matched case-insensitively. Multilingual plans are supported by matching the word stems in any language as long as the meaning aligns with the listed English trigger words.

| Tag | Trigger words | Default chain |
|---|---|---|
| `design` | architecture, design, choose, evaluate, RFC | `planner,architect` |
| `plan` | plan, breakdown, milestone | `planner` |
| `impl` | implement, build, add, create, port | `tdd-guide,<lang>-reviewer` |
| `test` | test, coverage, e2e, integration | `tdd-guide,e2e-runner` |
| `refactor` | refactor, cleanup, dedupe, split | `architect,refactor-cleaner,<lang>-reviewer` |
| `migration` | migrate, upgrade, rewrite, port | `architect,tdd-guide,<lang>-reviewer` |
| `db` | schema, migration, index, SQL, Postgres, alembic, sqlmodel | `database-reviewer,<lang>-reviewer` |
| `security` | encrypt, auth, secret, OWASP, PII | `security-reviewer,<lang>-reviewer` |
| `build` | build, compile, lint failure, CI | `<lang>-build-resolver` (falls back to `build-error-resolver`) |
| `docs` | docs, readme, codemap, changelog | `doc-updater` |
| `lookup` | lookup, reference, API usage | `docs-lookup` |
| `review` | review, audit, verify | `<lang>-reviewer,code-reviewer` |
| `loop` | loop, autonomous, watchdog | `loop-operator` |

Chain composition rules:
1. **Primary tag selection**: when a step matches multiple tags, the **first one in table order** (top of the table = highest priority) is the primary; the rest are secondaries. Composition rules 2 and 3 below handle specific multi-tag combinations explicitly; otherwise, append secondary chains in tag table order.
2. `impl` + `security` → `tdd-guide,<lang>-reviewer,security-reviewer`.
3. `impl` + `db` → `tdd-guide,database-reviewer,<lang>-reviewer`.
4. **Deduplicate** the resulting chain (preserve first occurrence). E.g. `review` + `lang=unknown` would yield `code-reviewer,code-reviewer` after rule 5; deduplication collapses it to `code-reviewer`.
5. `<lang>-reviewer` resolves to `code-reviewer` when `lang=unknown`.
6. `<lang>-build-resolver` resolves to `build-error-resolver` when `lang=unknown`. **Special case**: if Phase 0 set `pytorch=true`, use `pytorch-build-resolver` for `build` chains regardless of `<lang>`. There is no `python-build-resolver`; `--lang=python` without `pytorch=true` resolves to `build-error-resolver`.
7. **Zero-tag steps**: if no trigger word matches, set chain to `code-reviewer` and write `no tag matched; default review-only chain` under "Chain rationale".
8. Chain length ≤ 4 after deduplication. If exceeded, drop weakest tag (`lookup` and `docs` first).
9. Do not pair `planner` and `architect` in an `impl` chain (token waste). Pair them only on `design` steps.
10. Steps tagged `impl`, `refactor`, or `migration` end with a **reviewer-class** agent — any of `<lang>-reviewer`, `code-reviewer`, `security-reviewer`, or `database-reviewer`. The most domain-specific reviewer wins the tail position (e.g. rule 2's `impl+security` ends with `security-reviewer`; rule 3's `impl+db` ends with `<lang>-reviewer` because `database-reviewer` already gates the migration earlier in the chain). `test` and `build` steps are gated by their own validators (`e2e-runner` and the build resolver respectively) and do not require an additional reviewer.

### Phase 3 — Compress task description

Each emitted `<task description>` must:
- Be self-contained (the first agent does not need the plan document open).
- Start with `[Plan: <path>#step-<id>]`.
- Include 1–3 verifiable Acceptance criteria.
- Include a Scope guard (`Out of scope: ...`) **only if the plan declares one for this step**. Inherit verbatim. If the plan has no out-of-scope statement, omit the clause entirely — do not invent one.
- Be 200–600 characters; one line; embedded `"` escaped as `\"`; no literal newlines.

### Phase 4 — Output

Emit Markdown using **the form determined by `ECC_MODE`**. The output uses one form throughout — every `{ORCH_CMD}` and every agent name is rendered with the matching prefix from Phase 0. **Do not emit both forms; do not include "this is plugin form" / "strip the prefix" instructions in the rendered output.**

Concrete rendering rules:

- `{ORCH_CMD}` = `/everything-claude-code:orchestrate` under `plugin`, `/orchestrate` under `legacy`.
- `{AGENT(name)}` = `everything-claude-code:<name>` under `plugin`, `<name>` under `legacy`.
- The overview-table "Chain" column uses the same `{AGENT(name)}` rendering.
- Per-step bash blocks contain only the runnable command. **No `# plugin form` or `# legacy form` comments** — the form is implicit and uniform across the whole output.

Output structure:

````markdown
