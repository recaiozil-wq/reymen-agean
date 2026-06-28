---
skill_id: b2a436fda846
usage_count: 1
last_used: 2026-06-16
---
## Core Principle

Test what the user sees and does, not implementation details.

A test should:

- Render the component with the same providers it has in production
- Interact with it via accessible queries (role, label) and `userEvent`
- Assert visible output and observable side effects (callback fired, request sent)

A test should NOT:

- Inspect component state, props passed to children, or which hooks were called
- Mock React itself or framework hooks
- Assert on the number of renders or DOM structure beyond what affects users