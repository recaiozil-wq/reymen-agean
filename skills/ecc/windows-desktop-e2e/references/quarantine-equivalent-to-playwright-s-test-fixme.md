---
skill_id: 70e78ad2f276
usage_count: 1
last_used: 2026-06-16
---
# Quarantine — equivalent to Playwright's test.fixme()
@pytest.mark.skip(reason="Flaky: animation race on slow CI. Issue #42")
def test_animated_transition(self, app): ...