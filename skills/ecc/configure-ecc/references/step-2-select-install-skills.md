---
skill_id: 51465d8e27bc
usage_count: 1
last_used: 2026-06-16
---
## Step 2: Select & Install Skills

### 2a: Choose Scope (Core vs Niche)

Default to **Core (recommended for new users)** — copy `.agents/skills/*` plus `skills/search-first/` for research-first workflows. This bundle covers engineering, evals, verification, security, strategic compaction, frontend design, and Anthropic cross-functional skills (article-writing, content-engine, market-research, frontend-slides).

Use `AskUserQuestion` (single select):
```
Question: "Install core skills only, or include niche/framework packs?"
Options:
  - "Core only (recommended)" — "tdd, e2e, evals, verification, research-first, security, frontend patterns, compacting, cross-functional Anthropic skills"
  - "Core + selected niche" — "Add framework/domain-specific skills after core"
  - "Niche only" — "Skip core, install specific framework/domain skills"
Default: Core only
```

If the user chooses niche or core + niche, continue to category selection below and only include those niche skills they pick.

### 2b: Choose Skill Categories

There are 7 selectable category groups below. The detailed confirmation lists that follow cover 45 skills across 8 categories, plus 1 standalone template. Use `AskUserQuestion` with `multiSelect: true`:

```
Question: "Which skill categories do you want to install?"
Options:
  - "Framework & Language" — "Django, Laravel, Spring Boot, Quarkus, Go, Python, Java, Frontend, Backend patterns"
  - "Database" — "PostgreSQL, ClickHouse, JPA/Hibernate patterns"
  - "Workflow & Quality" — "TDD, verification, learning, security review, compaction"
  - "Research & APIs" — "Deep research, Exa search, Claude API patterns"
  - "Social & Content Distribution" — "X/Twitter API, crossposting alongside content-engine"
  - "Media Generation" — "fal.ai image/video/audio alongside VideoDB"
  - "Orchestration" — "dmux multi-agent workflows"
  - "All skills" — "Install every available skill"
```

### 2c: Confirm Individual Skills

For each selected category, print the full list of skills below and ask the user to confirm or deselect specific ones. If the list exceeds 4 items, print the list as text and use `AskUserQuestion` with an "Install all listed" option plus "Other" for the user to paste specific names.

**Category: Framework & Language (25 skills)**

| Skill | Description |
|-------|-------------|
| `backend-patterns` | Backend architecture, API design, server-side best practices for Node.js/Express/Next.js |
| `coding-standards` | Universal coding standards for TypeScript, JavaScript, React, Node.js |
| `django-patterns` | Django architecture, REST API with DRF, ORM, caching, signals, middleware |
| `django-security` | Django security: auth, CSRF, SQL injection, XSS prevention |
| `django-tdd` | Django testing with pytest-django, factory_boy, mocking, coverage |
| `django-verification` | Django verification loop: migrations, linting, tests, security scans |
| `laravel-patterns` | Laravel architecture patterns: routing, controllers, Eloquent, queues, caching |
| `laravel-security` | Laravel security: auth, policies, CSRF, mass assignment, rate limiting |
| `laravel-tdd` | Laravel testing with PHPUnit and Pest, factories, fakes, coverage |
| `laravel-verification` | Laravel verification: linting, static analysis, tests, security scans |
| `frontend-patterns` | React, Next.js, state management, performance, UI patterns |
| `frontend-slides` | Zero-dependency HTML presentations, style previews, and PPTX-to-web conversion |
| `golang-patterns` | Idiomatic Go patterns, conventions for robust Go applications |
| `golang-testing` | Go testing: table-driven tests, subtests, benchmarks, fuzzing |
| `java-coding-standards` | Java coding standards for Spring Boot and Quarkus: naming, immutability, Optional, streams, CDI |
| `python-patterns` | Pythonic idioms, PEP 8, type hints, best practices |
| `python-testing` | Python testing with pytest, TDD, fixtures, mocking, parametrization |
| `quarkus-patterns` | Quarkus architecture, Camel messaging, CDI services, Panache data access |
| `quarkus-security` | Quarkus security: JWT/OIDC, RBAC, input validation, secrets management |
| `quarkus-tdd` | Quarkus TDD with JUnit 5, Mockito, REST Assured, Camel testing |
| `quarkus-verification` | Quarkus verification: build, static analysis, tests, native compilation |
| `springboot-patterns` | Spring Boot architecture, REST API, layered services, caching, async |
| `springboot-security` | Spring Security: authn/authz, validation, CSRF, secrets, rate limiting |
| `springboot-tdd` | Spring Boot TDD with JUnit 5, Mockito, MockMvc, Testcontainers |
| `springboot-verification` | Spring Boot verification: build, static analysis, tests, security scans |

**Category: Database (3 skills)**

| Skill | Description |
|-------|-------------|
| `clickhouse-io` | ClickHouse patterns, query optimization, analytics, data engineering |
| `jpa-patterns` | JPA/Hibernate entity design, relationships, query optimization, transactions |
| `postgres-patterns` | PostgreSQL query optimization, schema design, indexing, security |

**Category: Workflow & Quality (8 skills)**

| Skill | Description |
|-------|-------------|
| `continuous-learning` | Legacy v1 Stop-hook session pattern extraction; prefer `continuous-learning-v2` for new installs |
| `continuous-learning-v2` | Instinct-based learning with confidence scoring, evolves into skills, agents, and optional legacy command shims |
| `eval-harness` | Formal evaluation framework for eval-driven development (EDD) |
| `iterative-retrieval` | Progressive context refinement for subagent context problem |
| `security-review` | Security checklist: auth, input, secrets, API, payment features |
| `strategic-compact` | Suggests manual context compaction at logical intervals |
| `tdd-workflow` | Enforces TDD with 80%+ coverage: unit, integration, E2E |
| `verification-loop` | Verification and quality loop patterns |

**Category: Business & Content (5 skills)**

| Skill | Description |
|-------|-------------|
| `article-writing` | Long-form writing in a supplied voice using notes, examples, or source docs |
| `content-engine` | Multi-platform social content, scripts, and repurposing workflows |
| `market-research` | Source-attributed market, competitor, fund, and technology research |
| `investor-materials` | Pitch decks, one-pagers, investor memos, and financial models |
| `investor-outreach` | Personalized investor cold emails, warm intros, and follow-ups |

**Category: Research & APIs (2 skills)**

| Skill | Description |
|-------|-------------|
| `deep-research` | Multi-source deep research using firecrawl and exa MCPs with cited reports |
| `exa-search` | Neural search via Exa MCP for web, code, company, and people research |

`claude-api` is an Anthropic canonical skill. Install it from [`anthropics/skills`](https://github.com/anthropics/skills) when you want the official Claude API workflow instead of an ECC-bundled copy.

**Category: Social & Content Distribution (2 skills)**

| Skill | Description |
|-------|-------------|
| `x-api` | X/Twitter API integration for posting, threads, search, and analytics |
| `crosspost` | Multi-platform content distribution with platform-native adaptation |

**Category: Media Generation (2 skills)**

| Skill | Description |
|-------|-------------|
| `fal-ai-media` | Unified AI media generation (image, video, audio) via fal.ai MCP |
| `video-editing` | AI-assisted video editing for cutting, structuring, and augmenting real footage |

**Category: Orchestration (1 skill)**

| Skill | Description |
|-------|-------------|
| `dmux-workflows` | Multi-agent orchestration using dmux for parallel agent sessions |

**Standalone**

| Skill | Description |
|-------|-------------|
| `docs/examples/project-guidelines-template.md` | Template for creating project-specific skills |

### 2d: Execute Installation

For each selected skill, copy the entire skill directory from the correct source root:

```bash