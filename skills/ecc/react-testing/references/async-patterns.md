---
skill_id: 8a3bf3715a8b
usage_count: 1
last_used: 2026-06-16
---
## Async Patterns

```tsx
// Element that appears after async work
expect(await screen.findByText("Loaded")).toBeInTheDocument();

// Side effect assertion
await waitFor(() => expect(saveSpy).toHaveBeenCalled());

// Element that should disappear
await waitForElementToBeRemoved(() => screen.queryByText("Loading"));
```

Never `setTimeout` + assertion — flaky. Use the matchers above.