---
name: ecc_autonomous-loops_references_next-steps
description: Next Steps
title: "Ecc Autonomous Loops References Next Steps"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Next Steps |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Next Steps
- Focus on rate limiting module next
- The mock setup in tests/helpers.ts can be reused
```

Claude reads this file at iteration start and updates it at iteration end. This bridges the context gap between independent `claude -p` invocations.

### CI Failure Recovery

When PR checks fail, Continuous Claude automatically:
1. Fetches the failed run ID via `gh run list`
2. Spawns a new `claude -p` with CI fix context
3. Claude inspects logs via `gh run view`, fixes code, commits, pushes
4. Re-waits for checks (up to `--ci-retry-max` attempts)

### Completion Signal

Claude can signal "I'm done" by outputting a magic phrase:

```bash
continuous-claude \
  --prompt "Fix all bugs in the issue tracker" \
  --completion-signal "CONTINUOUS_CLAUDE_PROJECT_COMPLETE" \
  --completion-threshold 3  # Stops after 3 consecutive signals
```

Three consecutive iterations signaling completion stops the loop, preventing wasted runs on finished work.

### Key Configuration

| Flag | Purpose |
|------|---------|
| `--max-runs N` | Stop after N successful iterations |
| `--max-cost $X` | Stop after spending $X |
| `--max-duration 2h` | Stop after time elapsed |
| `--merge-strategy squash` | squash, merge, or rebase |
| `--worktree <name>` | Parallel execution via git worktrees |
| `--disable-commits` | Dry-run mode (no git operations) |
| `--review-prompt "..."` | Add reviewer pass per iteration |
| `--ci-retry-max N` | Auto-fix CI failures (default: 1) |

---
