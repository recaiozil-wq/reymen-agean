---
skill_id: ccd1066343c9
usage_count: 1
last_used: 2026-06-16
---
## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GAN_MAX_ITERATIONS` | `15` | Maximum generator-evaluator cycles |
| `GAN_PASS_THRESHOLD` | `7.0` | Weighted score to pass (1-10) |
| `GAN_PLANNER_MODEL` | `opus` | Model for planning agent |
| `GAN_GENERATOR_MODEL` | `opus` | Model for generator agent |
| `GAN_EVALUATOR_MODEL` | `opus` | Model for evaluator agent |
| `GAN_EVAL_CRITERIA` | `design,originality,craft,functionality` | Comma-separated criteria |
| `GAN_DEV_SERVER_PORT` | `3000` | Port for the live app |
| `GAN_DEV_SERVER_CMD` | `npm run dev` | Command to start dev server |
| `GAN_PROJECT_DIR` | `.` | Project working directory |
| `GAN_SKIP_PLANNER` | `false` | Skip planner, use spec directly |
| `GAN_EVAL_MODE` | `playwright` | `playwright`, `screenshot`, or `code-only` |

### Evaluation Modes

| Mode | Tools | Best For |
|------|-------|----------|
| `playwright` | Browser MCP + live interaction | Full-stack apps with UI |
| `screenshot` | Screenshot + visual analysis | Static sites, design-only |
| `code-only` | Tests + linting + build | APIs, libraries, CLI tools |