---
skill_id: 35a30d27959f
usage_count: 1
last_used: 2026-06-16
---
## Best Practices

- **Set budgets before delegation**: When spawning sub-agents, attach a SpendingPolicy via your orchestration layer. Never give an agent unlimited spend.
- **Pin your dependencies**: Always specify an exact version in your MCP config (e.g., `agentwallet-sdk@6.0.0`). Verify package integrity before deploying to production.
- **Audit trails**: Use `list_transactions` in post-task hooks to log what was spent and why.
- **Fail closed**: If the payment tool is unreachable, block the paid action — don't fall back to unmetered access.
- **Pair with security-review**: Payment tools are high-privilege. Apply the same scrutiny as shell access.
- **Test with testnets first**: Use Base Sepolia for development; switch to Base mainnet for production.