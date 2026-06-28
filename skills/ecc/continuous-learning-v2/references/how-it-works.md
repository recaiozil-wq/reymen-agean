---
skill_id: 4f9625493343
usage_count: 1
last_used: 2026-06-16
---
## How It Works

```
Session Activity (in a git repo)
      |
      | Hooks capture prompts + tool use (100% reliable)
      | + detect project context (git remote / repo path)
      v
+---------------------------------------------+
|  projects/<project-hash>/observations.jsonl  |
|   (prompts, tool calls, outcomes, project)   |
+---------------------------------------------+
      |
      | Observer agent reads (background, Haiku)
      v
+---------------------------------------------+
|          PATTERN DETECTION                   |
|   * User corrections -> instinct             |
|   * Error resolutions -> instinct            |
|   * Repeated workflows -> instinct           |
|   * Scope decision: project or global?       |
+---------------------------------------------+
      |
      | Creates/updates
      v
+---------------------------------------------+
|  projects/<project-hash>/instincts/personal/ |
|   * prefer-functional.yaml (0.7) [project]   |
|   * use-react-hooks.yaml (0.9) [project]     |
+---------------------------------------------+
|  instincts/personal/  (GLOBAL)               |
|   * always-validate-input.yaml (0.85) [global]|
|   * grep-before-edit.yaml (0.6) [global]     |
+---------------------------------------------+
      |
      | /evolve clusters + /promote
      v
+---------------------------------------------+
|  projects/<hash>/evolved/ (project-scoped)   |
|  evolved/ (global)                           |
|   * commands/new-feature.md                  |
|   * skills/testing-workflow.md               |
|   * agents/refactor-specialist.md            |
+---------------------------------------------+
```