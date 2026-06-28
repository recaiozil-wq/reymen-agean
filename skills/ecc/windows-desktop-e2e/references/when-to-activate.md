---
skill_id: 98337030a4a3
usage_count: 1
last_used: 2026-06-16
---
## When to Activate

- Writing or running E2E tests for a Windows native desktop application
- Setting up a desktop GUI test suite from scratch
- Diagnosing flaky or failing desktop automation tests
- Adding testability (AutomationId, accessible names) to an existing app
- Integrating desktop E2E into a CI/CD pipeline (GitHub Actions `windows-latest`)

### When NOT to Use

- Web applications → use `e2e-testing` skill (Playwright)
- Electron / CEF / WebView2 apps → the HTML layer needs browser automation, not UIA
- Mobile apps → use platform-specific tools (UIAutomator, XCUITest)
- Pure unit or integration tests that don't need a running GUI