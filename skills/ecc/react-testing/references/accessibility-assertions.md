---
skill_id: 49b065a17648
usage_count: 1
last_used: 2026-06-16
---
## Accessibility Assertions

```tsx
import { axe, toHaveNoViolations } from "jest-axe"; // or vitest-axe
expect.extend(toHaveNoViolations);

test("UserCard has no a11y violations", async () => {
  const { container } = render(<UserCard user={mockUser} />);
  expect(await axe(container)).toHaveNoViolations();
});
```

Run axe in component tests for every interactive component. Catches:

- Missing labels on form inputs
- Invalid ARIA usage
- Poor color contrast (limited — JSDOM has no real CSS engine, so this works for inline styles only; visual contrast belongs in Playwright)
- Missing alt text on images
- Heading order violations

Cross-link: [skills/accessibility/SKILL.md](../accessibility/SKILL.md) for the broader a11y testing playbook.